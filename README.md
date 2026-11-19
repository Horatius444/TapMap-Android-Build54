# TapMap Android — Build 54 (Preserved Release)

A clean preservation repository for the verified ARM64 Android build of TapMap.

**Maintainer:** Onke Horatius Mwelase (@Horatius444)  
**Package:** `com.horatius.tapmap`  
**Architecture:** `arm64-v8a`  
**Build:** 54 (debug APK)

## Verified build record

- APK: `app-debug.apk`
- Size: 53,610,694 bytes (about 51.1 MiB)
- SHA-256: `0fd7a12183d4f3688aac30a13e809b5ae52c1e4448a5cb10ea0de841895a9f80`
- Build Actions run: [#44438669492](https://github.com/Horatius444/TapMap-Android/actions/runs/44438669492)
- Build source commit: `f19903e4a92173c7a3e95f38d1e90de287a1ce4e`

Build 54 was verified on a physical Android device. Live packet reception was confirmed using PCAPdroid UDP export to the local TapMap receiver at `127.0.0.1:5123`. PCAPdroid is a separate app and is not bundled.

## APK availability

The Actions artifact is temporary and expires on 17 February 2027. A permanent GitHub Release asset has **not yet been attached**. Keep an independent APK copy and verify it against the SHA-256 above. This repository currently contains the source and preservation records, not the binary APK asset.

## Source

The Android shell and key Python runtime files are included here. The complete source snapshot is pinned to the original development repository at commit [4d482d7](https://github.com/Horatius444/TapMap-Android/commit/4d482d7b4319f2cf20ab33eb4c232c09a4d5022a), with the build itself made from commit `f19903e4a92173c7a3e95f38d1e90de287a1ce4e`.

## Attribution

This is an Android adaptation of upstream TapMap by Ola Lie (@olalie), not a claim of ownership over the original software. See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md), [LICENSE](LICENSE), and [third-party notices](third_party/THIRD_PARTY_NOTICES.md).

**Status: Build 54 preserved.** Experimental builds are not substitutes for this verified APK.
