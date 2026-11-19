# TapMap Android — Build 54

A self-contained Android source repository for reconstructing the verified TapMap ARM64 Build 54.

- Application ID: `com.horatius.tapmap`
- ABI: `arm64-v8a`
- Build 54 source commit: `f19903e4a92173c7a3e95f38d1e90de287a1ce4e`
- Verified APK SHA-256: `0fd7a12183d4f3688aac30a13e809b5ae52c1e4448a5cb10ea0de841895a9f80`

## Repository contents

This repository contains the Android build project and its complete runtime input tree:

- `android/` — Gradle project, manifest, Java shell and Android resources.
- `src/` — complete Python application/runtime source tree and bundled assets used by Chaquopy.
- Root dependency manifests — Android Python packages and build/test requirements.
- `.github/workflows/android-build.yml` — reproducible ARM64 APK build workflow.
- Licensing, privacy, security and third-party notices.
- Build 54 preservation record.

The Android source and runtime files are committed here. **A clone of this repository does not require the former development repository.**

## Rebuild the APK

Build environment used by CI:
- JDK 17
- Android SDK platform 36
- Android Build Tools 36.0.0
- Gradle 8.13
- Python 3.13 (Chaquopy runtime)

From the repository root, run:

```bash
gradle -p android --no-daemon --stacktrace :app:assembleDebug
```

Output:

```
android/app/build/outputs/apk/debug/app-debug.apk
```

The Actions workflow builds the ARM64 debug APK on pushes affecting `android/**` or `src/**`, and can also be started manually from the Actions tab.

## Verified Build 54

Build 54 was installed and tested on a physical Android device. Live packet reception was confirmed using PCAPdroid UDP export to TapMap's local receiver at `127.0.0.1:5123`. PCAPdroid is a separate Android app and is not bundled.

The preserved APK is a debug build, 53,610,694 bytes. Verify a retained copy with:

```bash
sha256sum app-debug.apk
```

Expected digest:

```
0fd7a12183d4f3688aac30a13e809b5ae52c1e4448a5cb10ea0de841895a9f80
```

See [PRESERVED_BUILD_54.md](PRESERVED_BUILD_54.md) for the original artifact record and [RELEASE_UPLOAD.md](RELEASE_UPLOAD.md) for permanent release instructions.

## Attribution

TapMap Android is an Android adaptation of upstream TapMap. Original authorship and third-party licensing remain with their respective owners. See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md), [LICENSE](LICENSE), and [third_party/THIRD_PARTY_NOTICES.md](third_party/THIRD_PARTY_NOTICES.md).

Maintainer of this Android preservation: Onke Horatius Mwelase (@Horatius444).
