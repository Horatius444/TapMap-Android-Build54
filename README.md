# TapMap Android

TapMap is an Android network-activity visualisation app. It presents observed network connections in a live map and provides connection details, application attribution, network information and activity insights.

This repository contains the complete Android application project and the Python application/runtime source required to build it.

## What the app does

- Displays observed network connections on an interactive map.
- Shows connection details, including source/destination addresses, ports and protocols.
- Attributes captured traffic to Android applications when PCAPdroid supplies application metadata.
- Provides LAN/local network and open-port views.
- Includes connection history, significant-connection views and daily activity insights.
- Supports GeoIP databases for geographic network information.
- Provides settings and data-management controls within the app.

### Live traffic input on Android

The Android packet collector receives PCAPdroid's UDP PCAP export on the device loopback interface:

```
127.0.0.1:5123
```

Install **PCAPdroid** separately and configure its UDP exporter to send to `127.0.0.1:5123`. PCAPdroid is not bundled in this repository or APK. Without an active packet feed, the app can open but will not receive live captured traffic through this integration.

## Project structure

```
.
├── android/                  # Android app and Gradle project
├── src/                      # Python application and runtime assets
├── third_party/              # Bundled third-party components/notices
├── requirements-android.txt  # Android Python runtime dependencies
├── requirements.txt          # Python project dependencies
├── requirements-tests.txt    # Python test dependencies
├── requirements-build.txt    # Python build dependencies
└── .github/workflows/        # Automated Android build
```

The Android module loads the Python application from `src/` using Chaquopy. The Android-specific Python dependencies are declared in `requirements-android.txt`.

## Build the Android APK

### Build environment

- JDK 17
- Gradle 8.13
- Android SDK Platform 36
- Android SDK Build-Tools 36.0.0
- Android NDK as required by the Chaquopy Android build
- Internet connection for downloading Gradle, Android and Python build dependencies

The Android application is configured for **ARM64 (`arm64-v8a`)**, with minimum Android API 24 and target API 35.

### 1. Clone the repository

```bash
git clone https://github.com/Horatius444/TapMap-Android-Build54.git
cd TapMap-Android-Build54
```

### 2. Install Android SDK components

```bash
sdkmanager "platforms;android-36" "build-tools;36.0.0" "platform-tools"
```

Make sure `JAVA_HOME`, `ANDROID_HOME` (or `ANDROID_SDK_ROOT`) and the SDK tools are available in your shell.

### 3. Build

From the repository root:

```bash
gradle -p android --no-daemon --stacktrace :app:assembleDebug
```

### 4. APK output

The generated APK is:

```
android/app/build/outputs/apk/debug/app-debug.apk
```

## Automated build

GitHub Actions builds the ARM64 debug APK using the same Gradle task. To start a build manually:

1. Open the repository's **Actions** tab.
2. Select **TapMap Android Build**.
3. Select **Run workflow**.

The resulting APK is uploaded as a workflow artifact.

## Main implementation

- **Android shell:** Java activity, Android WebView, loading/error interface, Android document picker and PCAPdroid integration.
- **Python application:** Dash interface, network model, GeoIP services, connection analysis, persistence and insights.
- **Local interface service:** the Android app hosts the TapMap interface locally on the device and loads it in its WebView.
- **Runtime dependencies:** installed into the Android package by Chaquopy from the Android requirements manifest.

## Licensing

Review [LICENSE](LICENSE) and [third_party/THIRD_PARTY_NOTICES.md](third_party/THIRD_PARTY_NOTICES.md) for licensing information covering the project and bundled components.
