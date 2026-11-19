# Release upload checklist — Build 54

The verified APK is a debug ARM64 build. Before calling this a complete permanent release, attach the APK to a GitHub Release.

1. Open this repository and choose **Releases** → **Create a new release**.
2. Create tag `v1.0.0-build54` on `main`.
3. Release title: `TapMap Android — Build 54 (ARM64)`.
4. Attach the file `app-debug.apk` (53,610,694 bytes).
5. Publish the release.
6. Verify the uploaded asset SHA-256 is:

`0fd7a12183d4f3688aac30a13e809b5ae52c1e4448a5cb10ea0de841895a9f80`

Do not attach a different APK or replace Build 54 with an experimental build.

The APK is not yet attached to this repository. The original Actions artifact is temporary and was reported to expire on 17 February 2027.
