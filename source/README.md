# Source archive

The v0.1 ZIP is stored as seven binary segments in `parts/part-01.bin` through `parts/part-07.bin` to preserve its exact bytes.

On Windows, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\source\assemble.ps1
```

The script reconstructs `reqable-bridge-source-v0.1.zip`, verifies its SHA-256, extracts it to `source/extracted/`, and applies the Compose import compatibility fix to the extracted Android source.

GitHub Actions performs the same reconstruction and fix automatically before building and testing.
