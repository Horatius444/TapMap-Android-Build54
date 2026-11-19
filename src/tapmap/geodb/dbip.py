"""DB-IP-specific GeoDB operations for TapMap."""

from __future__ import annotations

import gzip
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import maxminddb
import requests


@dataclass(frozen=True)
class _RemoteDatabaseInfo:
    """Remote DB-IP release information for one database."""

    version: str
    download_url: str


ProgressCallback = Callable[[str], None]


class DbIpProvider:
    """Handle DB-IP provider-specific operations."""

    CITY_PAGE_URL = "https://db-ip.com/db/download/ip-to-city-lite"
    ASN_PAGE_URL = "https://db-ip.com/db/download/ip-to-asn-lite"
    DOWNLOAD_URL = "https://download.db-ip.com/free/dbip-{name}-lite-{version}.mmdb.gz"

    CITY_FILENAME = "DBIP-City.mmdb"
    ASN_FILENAME = "DBIP-ASN.mmdb"
    USER_AGENT = "TapMap/1.0 (GeoIP database installer)"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)

    @property
    def city_path(self) -> Path:
        return self.data_dir / self.CITY_FILENAME

    @property
    def asn_path(self) -> Path:
        return self.data_dir / self.ASN_FILENAME

    @staticmethod
    def _read_build_epoch(path: Path) -> int | None:
        if not path.exists():
            return None
        try:
            with maxminddb.open_database(path) as reader:
                build_epoch = reader.metadata().build_epoch
        except Exception:
            return None
        return int(build_epoch) if isinstance(build_epoch, int) else None

    @staticmethod
    def _epoch_to_month_key(epoch: int | None) -> str | None:
        if epoch is None:
            return None
        return datetime.fromtimestamp(epoch, tz=UTC).strftime("%Y-%m")

    @staticmethod
    def _month_key_to_display_date(month_key: str | None) -> str | None:
        return f"{month_key}-01" if month_key else None

    def get_local_status(self) -> dict[str, Any]:
        city_installed = self.city_path.exists()
        asn_installed = self.asn_path.exists()
        city_epoch = self._read_build_epoch(self.city_path)
        asn_epoch = self._read_build_epoch(self.asn_path)
        city_month = self._epoch_to_month_key(city_epoch)
        asn_month = self._epoch_to_month_key(asn_epoch)
        local_version = min(city_month, asn_month) if city_month and asn_month else None
        return {
            "city_installed": city_installed,
            "asn_installed": asn_installed,
            "city_valid": city_epoch is not None,
            "asn_valid": asn_epoch is not None,
            "local_version": local_version,
            "local_city_date": self._month_key_to_display_date(city_month),
            "local_asn_date": self._month_key_to_display_date(asn_month),
            "local_display_date": self._month_key_to_display_date(local_version),
        }

    @staticmethod
    def _extract_latest_remote_info(page_text: str, database_name: str) -> _RemoteDatabaseInfo:
        pattern = (
            rf"https://download\.db-ip\.com/free/"
            rf"dbip-{re.escape(database_name)}-lite-(\d{{4}}-\d{{2}})\.mmdb\.gz"
        )
        matches = re.findall(pattern, page_text, flags=re.IGNORECASE)
        if not matches:
            raise RuntimeError(
                f"DB-IP's {database_name.upper()} download page did not contain a release link."
            )
        version = max(matches)
        return _RemoteDatabaseInfo(
            version=version,
            download_url=DbIpProvider.DOWNLOAD_URL.format(name=database_name, version=version),
        )

    def _get_remote_info(self, page_url: str, database_name: str) -> _RemoteDatabaseInfo:
        try:
            response = requests.get(
                page_url,
                timeout=(20, 45),
                headers={"User-Agent": self.USER_AGENT},
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "unknown"
            raise RuntimeError(
                f"DB-IP {database_name.upper()} release page returned HTTP {code}."
            ) from None
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not reach DB-IP's {database_name.upper()} release page: {exc}"
            ) from None

        try:
            return self._extract_latest_remote_info(response.text, database_name)
        except RuntimeError as exc:
            raise RuntimeError(
                f"{exc} The provider may have changed its download page."
            ) from None

    def fetch_remote_version(self) -> str:
        city = self._get_remote_info(self.CITY_PAGE_URL, "city")
        asn = self._get_remote_info(self.ASN_PAGE_URL, "asn")
        return min(city.version, asn.version)

    @staticmethod
    def _download_and_extract_gz(
        download_url: str,
        target_path: Path,
        label: str,
        progress: ProgressCallback | None = None,
    ) -> Path:
        """Stream a compressed database to disk, then extract without buffering it in RAM."""
        gz_path = target_path.with_suffix(".mmdb.gz")
        temp_target = target_path.with_name(target_path.name + ".tmp")
        headers = {"User-Agent": DbIpProvider.USER_AGENT}

        try:
            if progress:
                progress(f"Downloading {label} database…")
            with requests.get(
                download_url,
                timeout=(30, 240),
                headers=headers,
                stream=True,
            ) as response:
                response.raise_for_status()
                total = int(response.headers.get("Content-Length", "0") or 0)
                downloaded = 0
                with gz_path.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=1024 * 256):
                        if not chunk:
                            continue
                        output.write(chunk)
                        downloaded += len(chunk)
                        if progress and total:
                            progress(
                                f"Downloading {label}: {downloaded / 1048576:.1f} / "
                                f"{total / 1048576:.1f} MB"
                            )
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "unknown"
            gz_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"DB-IP {label} download returned HTTP {code}."
            ) from None
        except requests.RequestException as exc:
            gz_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"Network error while downloading DB-IP {label}: {exc}"
            ) from None
        except OSError as exc:
            gz_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"Could not save the DB-IP {label} download: {exc}"
            ) from None

        try:
            if progress:
                progress(f"Extracting {label} database…")
            with gzip.open(gz_path, "rb") as source, temp_target.open("wb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
            if temp_target.stat().st_size == 0:
                raise RuntimeError(f"The downloaded DB-IP {label} database is empty.")
            temp_target.replace(target_path)
        except (OSError, EOFError, gzip.BadGzipFile) as exc:
            temp_target.unlink(missing_ok=True)
            raise RuntimeError(
                f"Could not extract the DB-IP {label} database: {exc}"
            ) from None
        finally:
            gz_path.unlink(missing_ok=True)

        if DbIpProvider._read_build_epoch(target_path) is None:
            target_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"The DB-IP {label} file downloaded, but it is not a valid MMDB database."
            )
        if progress:
            progress(f"{label} database extracted and validated.")
        return target_path

    def download_pair_to(
        self,
        target_dir: Path,
        progress: ProgressCallback | None = None,
    ) -> tuple[Path, Path]:
        """Download and validate DB-IP City and ASN databases into target_dir."""
        target = Path(target_dir)
        target.mkdir(parents=True, exist_ok=True)
        if progress:
            progress("Checking DB-IP release information…")
        city_info = self._get_remote_info(self.CITY_PAGE_URL, "city")
        asn_info = self._get_remote_info(self.ASN_PAGE_URL, "asn")
        city_path = self._download_and_extract_gz(
            city_info.download_url,
            target / self.CITY_FILENAME,
            "City",
            progress,
        )
        asn_path = self._download_and_extract_gz(
            asn_info.download_url,
            target / self.ASN_FILENAME,
            "ASN",
            progress,
        )
        return city_path, asn_path
