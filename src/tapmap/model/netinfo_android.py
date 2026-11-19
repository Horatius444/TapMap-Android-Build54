from __future__ import annotations

import socket
import struct
import threading
import time

from typing import Any


class AndroidNetInfo:
    """
    Android network monitor using PCAPdroid UDP Exporter.

    Receives packet records locally and builds a table of observed
    network flows. Application identity comes from PCAPdroid metadata.

    This represents observed traffic, not every open Android socket.
    """

    HOST = "127.0.0.1"
    PORT = 5123
    MAX_FLOWS = 3000
    FLOW_TTL = 600

    def __init__(
        self,
        allowed_statuses: set[str] | None = None,
    ):
        self.allowed_statuses = allowed_statuses

        self._lock = threading.RLock()
        self._flows = {}
        self._running = True
        self._socket = None
        self._thread = threading.Thread(
            target=self._receive_loop,
            name="TapMap-PCAPdroid",
            daemon=True,
        )
        self._thread.start()

    def get_data(self) -> list[dict[str, Any]]:
        now = time.time()

        with self._lock:
            expired = [
                key for key, item in self._flows.items()
                if now - item["_seen"] > self.FLOW_TTL
            ]

            for key in expired:
                self._flows.pop(key, None)

            return [
                {
                    key: value
                    for key, value in item.items()
                    if not key.startswith("_")
                }
                for item in sorted(
                    self._flows.values(),
                    key=lambda x: x["_seen"],
                    reverse=True,
                )
            ]

    def close(self):
        self._running = False

        sock = self._socket
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass

        if self._thread.is_alive() and threading.current_thread() is not self._thread:
            self._thread.join(timeout=2.0)

    def _receive_loop(self):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        self._socket = sock

        try:
            sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )
            sock.bind((self.HOST, self.PORT))
            sock.settimeout(1.0)

            while self._running:
                try:
                    data, _ = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                except OSError:
                    break

                try:
                    self._process_datagram(data)
                except Exception:
                    continue

        except OSError:
            # The UI can still start. Capture status will remain empty
            # if another process owns the collector port.
            pass

        finally:
            try:
                sock.close()
            except OSError:
                pass

    def _process_datagram(self, data: bytes):
        # PCAPdroid can send its 24-byte PCAP file header first.
        if len(data) == 24 and data[:4] in (
            bytes.fromhex("d4c3b2a1"),
            bytes.fromhex("a1b2c3d4"),
            bytes.fromhex("4d3cb2a1"),
            bytes.fromhex("a1b23c4d"),
        ):
            return

        # UDP exporter datagrams contain PCAP records.
        if len(data) < 16:
            return

        try:
            ts_sec, ts_usec, caplen, original_len = (
                struct.unpack("<IIII", data[:16])
            )
        except struct.error:
            return

        if caplen <= 0 or caplen > len(data) - 16:
            return

        packet = data[16:16 + caplen]
        self._decode_packet(packet)

    def _decode_packet(self, frame: bytes):
        if len(frame) < 20:
            return

        uid = None
        package = "Unknown application"

        # PCAPdroid extension trailer:
        # magic(4), UID(4), package name(20), plus FCS(4).
        magic = bytes.fromhex("01072021")

        trailer_pos = frame.rfind(magic)

        if trailer_pos >= 0 and len(frame) - trailer_pos >= 28:
            try:
                uid = struct.unpack(
                    ">i", frame[trailer_pos + 4:trailer_pos + 8]
                )[0]

                raw_name = frame[
                    trailer_pos + 8:trailer_pos + 28
                ]

                package = (
                    raw_name.split(b"\0", 1)[0]
                    .decode("utf-8", errors="replace")
                    or "Unknown application"
                )

                # Extension packets use a synthetic Ethernet frame.
                frame = frame[14:trailer_pos]

            except (struct.error, IndexError):
                return

        else:
            # PCAPdroid may export raw IP packets without extensions.
            # Also accept Ethernet frames without metadata.
            if len(frame) >= 14:
                ethertype = struct.unpack(
                    ">H", frame[12:14]
                )[0]

                if ethertype in (0x0800, 0x86DD):
                    frame = frame[14:]

        if not frame:
            return

        version = frame[0] >> 4

        if version == 4:
            result = self._decode_ipv4(frame)
        elif version == 6:
            result = self._decode_ipv6(frame)
        else:
            return

        if result is None:
            return

        proto, src, sport, dst, dport, tcp_flags = result

        self._record_flow(
            proto,
            src,
            sport,
            dst,
            dport,
            tcp_flags,
            uid,
            package,
        )

    def _decode_ipv4(self, packet):
        if len(packet) < 20:
            return None

        ihl = (packet[0] & 15) * 4

        if ihl < 20 or len(packet) < ihl:
            return None

        # Ignore fragmented packets that are not first fragments.
        fragment = struct.unpack(">H", packet[6:8])[0]
        if fragment & 0x1FFF:
            return None

        proto = packet[9]
        src = socket.inet_ntop(socket.AF_INET, packet[12:16])
        dst = socket.inet_ntop(socket.AF_INET, packet[16:20])

        return self._decode_transport(
            packet[ihl:], proto, src, dst
        )

    def _decode_ipv6(self, packet):
        if len(packet) < 40:
            return None

        src = socket.inet_ntop(
            socket.AF_INET6, packet[8:24]
        )
        dst = socket.inet_ntop(
            socket.AF_INET6, packet[24:40]
        )

        next_header = packet[6]
        offset = 40

        # Walk common IPv6 extension headers.
        while next_header in (0, 43, 60, 44, 51):
            if len(packet) < offset + 2:
                return None

            current = next_header
            next_header = packet[offset]

            if current == 44:
                fragment = struct.unpack(
                    ">H", packet[offset + 2:offset + 4]
                )[0]
                if fragment & 0xFFF8:
                    return None
                size = 8

            elif current == 51:
                size = (packet[offset + 1] + 2) * 4

            else:
                size = (packet[offset + 1] + 1) * 8

            offset += size

            if offset > len(packet):
                return None

        return self._decode_transport(
            packet[offset:], next_header, src, dst
        )

    def _decode_transport(self, data, proto, src, dst):
        if proto not in (6, 17):
            return None

        if len(data) < 4:
            return None

        sport, dport = struct.unpack(">HH", data[:4])

        flags = 0

        if proto == 6 and len(data) >= 14:
            flags = data[13]

        return (
            "tcp" if proto == 6 else "udp",
            src,
            sport,
            dst,
            dport,
            flags,
        )

    def _record_flow(
        self,
        proto,
        src,
        sport,
        dst,
        dport,
        flags,
        uid,
        package,
    ):
        # Canonical direction-independent flow key.
        forward = (src, sport, dst, dport)
        reverse = (dst, dport, src, sport)

        if forward <= reverse:
            key = (proto,) + forward
            local_ip, local_port = src, sport
            remote_ip, remote_port = dst, dport
        else:
            key = (proto,) + reverse
            local_ip, local_port = dst, dport
            remote_ip, remote_port = src, sport

        if proto == "udp":
            status = "NONE"
        elif flags & 0x04:
            status = "CLOSED"
        elif flags & 0x01:
            status = "FIN_WAIT"
        elif flags & 0x02:
            status = "SYN_SENT"
        else:
            status = "ESTABLISHED"

        now = time.time()

        with self._lock:
            item = self._flows.get(key)

            if item is None:
                item = {
                    "pid": None,
                    "proto": proto,
                    "status": status,
                    "family": (
                        "IPv6" if ":" in local_ip else "IPv4"
                    ),
                    "type": "SOCK_STREAM" if proto == "tcp"
                    else "SOCK_DGRAM",
                    "laddr_ip": local_ip,
                    "laddr_port": local_port,
                    "raddr_ip": remote_ip,
                    "raddr_port": remote_port,
                    "process_status": (
                        "OK" if package != "Unknown application"
                        else "Unknown"
                    ),
                    "process_label": package,
                    "process_name": package,
                    "exe": package,
                    "cmdline": None,
                    "android_uid": uid,
                    "_seen": now,
                }

                self._flows[key] = item

            else:
                item["_seen"] = now
                item["status"] = status

                if uid is not None:
                    item["android_uid"] = uid

                if package != "Unknown application":
                    item["process_label"] = package
                    item["process_name"] = package
                    item["exe"] = package
                    item["process_status"] = "OK"

            if len(self._flows) > self.MAX_FLOWS:
                oldest = sorted(
                    self._flows,
                    key=lambda k: self._flows[k]["_seen"],
                )[:len(self._flows) - self.MAX_FLOWS]

                for old_key in oldest:
                    self._flows.pop(old_key, None)
