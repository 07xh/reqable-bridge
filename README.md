# Reqable Bridge

Windows Reqable capture → Android hotspot receiver, with phone-side start/pause control for Reqable.

## Source bundle

The v0.1 source bundle is available in the ChatGPT conversation as **Reqable Bridge v0.1 source ZIP**. Upload that ZIP to this repository at:

`source/reqable-bridge-source-v0.1.zip`

The archive contains the complete Android and Windows source projects.

## What it does

- Windows bridge configures Reqable Report Server and exposes authenticated start/stop controls.
- Android receiver accepts completed HTTP sessions as HAR JSON over the phone hotspot, decompresses Gzip, and stores records locally in SQLite.
- Phone can request Windows bridge to start or stop Reqable live capture.

## Important limitation

This is near-real-time forwarding of completed HTTP sessions, not a raw TCP/IP packet mirror. Reqable Report Server does not retry failed uploads. The receiver and control bridge must be reachable over the hotspot network.

## Build and verification

After the source ZIP is uploaded to `source/`, GitHub Actions builds a debug APK and runs Windows bridge tests. Physical-device hotspot connectivity and end-to-end Reqable transfer still require validation on the target devices.

## Security

Do not commit `config.json`, HAR files, packet captures, SQLite databases, access tokens, or real traffic exports. Captured traffic may contain cookies and credentials. Keep the repository private if you plan to store real capture samples or device-specific configuration.
