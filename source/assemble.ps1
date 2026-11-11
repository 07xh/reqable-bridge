$ErrorActionPreference = "Stop"

$partsDir = Join-Path $PSScriptRoot "parts"
$parts = Get-ChildItem -LiteralPath $partsDir -Filter "part-*.bin" | Sort-Object Name
if ($parts.Count -ne 7) {
    throw "Expected 7 source archive segments, found $($parts.Count)."
}

$zipPath = Join-Path $PSScriptRoot "reqable-bridge-source-v0.1.zip"
$stream = [System.IO.File]::Create($zipPath)
try {
    foreach ($part in $parts) {
        $bytes = [System.IO.File]::ReadAllBytes($part.FullName)
        $stream.Write($bytes, 0, $bytes.Length)
    }
}
finally {
    $stream.Dispose()
}

$expected = "50e8eaff4491a78d71c2371f37ff7f3f2be16a6924b85c68aeef9ae826e824b9"
$actual = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
    throw "Source archive SHA-256 mismatch. Expected $expected, got $actual."
}

$destination = Join-Path $PSScriptRoot "extracted"
if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
}
Expand-Archive -LiteralPath $zipPath -DestinationPath $destination -Force
Write-Host "Source archive verified and extracted to: $destination"
