# Source archive

The v0.1 ZIP is stored as seven binary segments in `parts/part-01.bin` through `parts/part-07.bin` to preserve its exact bytes.

On Windows, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\source\assemble.ps1
```

The script reconstructs `reqable-bridge-source-v0.1.zip`, verifies its SHA-256, and extracts it to `source/extracted/`.

GitHub Actions performs the same reconstruction automatically before building and testing.
