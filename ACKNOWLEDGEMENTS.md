# Acknowledgements and attribution

TapMap Android adapts existing open-source software and uses tools and libraries maintained by other developers. Their work is acknowledged here; this project does not claim authorship of those upstream components.

## Original TapMap

- **Project:** TapMap
- **Original developer:** Ola Lie (`olalie`)
- **Upstream repository:** https://github.com/olalie/tapmap
- **License:** MIT
- **Copyright notice:** Copyright (c) 2026 Ola Lie

The original TapMap Python application, map/interface implementation, data models, GeoIP integration, and substantial supporting code originate from the upstream project. Its MIT license is retained in this repository. The original copyright and license notice must remain with copies or substantial portions of that software.

## Android adaptation and integration

- **Maintainer of this Android adaptation:** Onke Horatius Mwelase (`Horatius444`).
- **Android-specific work:** Android application shell, Chaquopy packaging configuration, Android-specific network collection integration, PCAPdroid capture-control integration, Android file-picker integration, and related build/configuration work.
- **Preserved build:** GitHub Actions Build 54, source commit `f19903e4a92173c7a3e95f38d1e90de287a1ce4e`.

These statements describe the Android-specific adaptation work; they do not transfer ownership of upstream TapMap or third-party components.

## PCAPdroid

- **Project:** PCAPdroid
- **Repository:** https://github.com/emanuele-f/PCAPdroid
- **Role:** External Android packet-capture application. TapMap invokes its app-integration control interface and receives exported packet/flow data locally.
- PCAPdroid is a separate application and is not bundled into this APK. Refer to its repository for its own authorship and license terms.

## Build and runtime technologies

- **Android platform, SDK and WebView:** https://developer.android.com/
- **Gradle build system:** https://gradle.org/
- **Chaquopy Python-for-Android plugin:** https://chaquo.com/chaquopy/
- **Python:** https://www.python.org/
- **Dash:** https://github.com/plotly/dash
- **Plotly.py:** https://github.com/plotly/plotly.py
- **pycountry:** https://github.com/pycountry/pycountry
- **maxminddb Python reader:** https://github.com/maxmind/MaxMind-DB-Reader-python
- **Requests:** https://github.com/psf/requests
- **Certifi:** https://github.com/certifi/python-certifi

Exact Android Python dependency pins are recorded in `android/app/requirements-android.txt`.

## Other bundled upstream material

The original TapMap source includes third-party assets and notices. See [third_party/THIRD_PARTY_NOTICES.md](third_party/THIRD_PARTY_NOTICES.md) and [src/tapmap/assets/TwemojiCountryFlags-LICENSE.md](src/tapmap/assets/TwemojiCountryFlags-LICENSE.md) for the respective owners, sources and licenses.

## No implied endorsement

Acknowledgement does not imply that any upstream author, project, company or organization endorses TapMap Android or this adaptation. Each component remains subject to its own license and terms.
