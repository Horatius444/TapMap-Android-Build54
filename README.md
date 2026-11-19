# TapMap Android — Build 54

An Android source repository for rebuilding and preserving the verified TapMap Build 54 application.

This repository contains the Android project, Python runtime source, bundled application assets, dependency manifests, and CI build workflow. The deleted development repository is **not** required.

## Build identity

| Item | Value |
|---|---|
| Android application ID | `com.horatius.tapmap` |
| App version | `0.1.0` (version code `1`) |
| Android minimum SDK | API 24 |
| Android target SDK | API 35 |
| Compile SDK | API 36 |
| Native ABI | `arm64-v8a` |
| Python runtime (Chaquopy) | Python 3.13 |
| Historical Build 54 source commit | `f19903e4a92173c7a3e95f38d1e90de287a1ce4e` |

The historical source commit identifies the verified Build 54 development snapshot. The current `main` branch is the preserved, self-contained reconstruction repository.

## Repository layout

- `android/` — Android Gradle project, application module, manifest, Java code and Android resources.
- `src/` — Python application package and runtime assets loaded by the Android build.
- `android/app/requirements-android.txt` — Python packages installed into the Android app by Chaquopy.
- `requirements-android.txt` — root-level Android runtime dependency manifest.
- `requirements.txt`, `requirements-tests.txt`, `requirements-build.txt` — Python development, test and build dependencies.
- `third_party/` — bundled third-party components and their notices.
- `.github/workflows/android-build.yml` — automated ARM64 debug APK build.
- `PRESERVED_BUILD_54.md` — record of the original device-tested APK and its checksum.
- `ACKNOWLEDGEMENTS.md`, `LICENSE`, `PRIVACY.md`, `SECURITY.md` — attribution, licensing, privacy and security information.

## Rebuild the Android APK

### Requirements

Use the following build environment:

- JDK 17
- Gradle 8.13
- Android SDK Platform 36
- Android SDK Build-Tools 36.0.0
- Python 3.13 available to the build environment (as configured in CI)
- Internet access during the initial build so Gradle, Android and Python dependencies can be downloaded

This repository currently uses a system-installed Gradle command; it does not include a Gradle Wrapper.

### Build steps

1. Clone this repository:

   ```bash
   git clone https://github.com/Horatius444/TapMap-Android-Build54.git
   cd TapMap-Android-Build54
   ```

2. Make sure the required Android SDK packages are installed:

   ```bash
   sdkmanager "platforms;android-36" "build-tools;36.0.0" "platform-tools"
   ```

3. Confirm that Java 17, Gradle 8.13 and the Android SDK are available in your environment. Set `ANDROID_HOME` or `ANDROID_SDK_ROOT` if your SDK is not in the standard location.

4. Build the debug APK from the repository root:

   ```bash
   gradle -p android --no-daemon --stacktrace :app:assembleDebug
   ```

5. Find the generated APK here:

   ```
   android/app/build/outputs/apk/debug/app-debug.apk
   ```

The Android Gradle build downloads and installs the Python packages declared for the app through Chaquopy. The first build therefore requires network access. Once dependencies are cached, Gradle may be able to reuse them for later builds.

### Automated build

The GitHub Actions workflow uses JDK 17, Python 3.13, Gradle 8.13, Android SDK Platform 36 and Build-Tools 36.0.0. It runs the same Gradle build command and uploads the resulting APK as an Actions artifact.

To start a build manually, open the repository's **Actions** tab, select **TapMap Android Build**, and choose **Run workflow**. Actions artifacts are temporary and expire according to the repository's artifact-retention settings; they are not permanent release downloads.

## Build 54 device verification

Build 54 was installed and tested on a physical Android device. Live packet reception was confirmed by exporting UDP packets from **PCAPdroid** to TapMap's local receiver at:

```
127.0.0.1:5123
```

PCAPdroid is a separate Android application. It is not bundled with TapMap and must be installed and configured separately for this packet-capture workflow.

The original device-tested Build 54 APK record is:

- Filename: `app-debug.apk`
- Size: `53,610,694` bytes
- SHA-256: `0fd7a12183d4f3688aac30a13e809b5ae52c1e4448a5cb10ea0de841895a9f80`

To verify a retained copy of that **original APK**, run:

```bash
sha256sum app-debug.apk
```

The checksum above identifies the preserved original binary. A newly rebuilt APK may not be byte-for-byte identical, even when it is built successfully from this source.

See [PRESERVED_BUILD_54.md](PRESERVED_BUILD_54.md) for the full preservation record.

## Scope and limitations

- The configured Android build targets `arm64-v8a`; this repository does not claim to produce a universal APK for every Android CPU architecture.
- The CI workflow builds a debug APK. A separately configured and securely signed release build is not provided by this workflow.
- Successful CI compilation confirms that the project builds; it does not replace installation and live packet-reception testing on a physical device.
- PCAPdroid is an external dependency for the documented packet-export test.

## Licensing and attribution

TapMap Android is an Android adaptation of upstream TapMap. Original authorship and third-party licensing remain with their respective owners. Review [LICENSE](LICENSE), [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md), and [third_party/THIRD_PARTY_NOTICES.md](third_party/THIRD_PARTY_NOTICES.md) before redistributing any part of the project.

Maintainer of this Android preservation: **Onke Horatius Mwelase** ([@Horatius444](https://github.com/Horatius444)).
