# Reqable Bridge

Windows Reqable capture → Android hotspot receiver, with phone-side start/pause control for Reqable.

## Source

The complete v0.1 source archive is stored losslessly as seven ordered binary segments in `source/parts/`. Rebuild and extract it on Windows with:

```powershell
powershell -ExecutionPolicy Bypass -File .\source\assemble.ps1
```

The script verifies the reconstructed archive SHA-256, extracts it, and applies the Android Compose import compatibility fix required by the current Compose toolchain.

## What it does

- Windows bridge configures Reqable Report Server and exposes authenticated start/stop controls.
- Android receiver accepts completed HTTP sessions as HAR JSON over the phone hotspot, decompresses Gzip, and stores records locally in SQLite.
- Phone can request Windows bridge to start or stop Reqable live capture.

## Important limitation

This is near-real-time forwarding of completed HTTP sessions, not a raw TCP/IP packet mirror. Reqable Report Server does not retry failed uploads. The receiver and control bridge must be reachable over the hotspot network.

## Build and verification

GitHub Actions assembles the source archive, applies the same Compose import fix, builds a debug APK, and runs Windows bridge tests. Physical-device hotspot connectivity and end-to-end Reqable transfer still require validation on the target devices.

## Security

Do not commit `config.json`, HAR files, packet captures, SQLite databases, access tokens, or real traffic exports. Captured traffic may contain cookies and credentials. Keep the repository private if you plan to store real capture samples or device-specific configuration.
