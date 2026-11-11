param(
    [string]$Destination = (Join-Path $PSScriptRoot "extracted")
)

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

if (Test-Path -LiteralPath $Destination) {
    Remove-Item -LiteralPath $Destination -Recurse -Force
}
Expand-Archive -LiteralPath $zipPath -DestinationPath $Destination -Force

$mainActivity = Join-Path $Destination "reqable-bridge\android\app\src\main\java\com\reqable\bridge\MainActivity.kt"
if (-not (Test-Path -LiteralPath $mainActivity)) {
    throw "Android MainActivity.kt was not found after extraction."
}
$content = [System.IO.File]::ReadAllText($mainActivity)
$content = [regex]::Replace($content, '(?m)^import androidx\.compose\.foundation\.layout\.weight\r?\n', '')
$content = $content.Replace(
    "import androidx.compose.foundation.text.SelectionContainer",
    "import androidx.compose.foundation.text.selection.SelectionContainer"
)
if ($content -match 'import androidx\.compose\.foundation\.layout\.weight') {
    throw "Compose weight import compatibility fix did not apply."
}
if ($content -notmatch 'import androidx\.compose\.foundation\.text\.selection\.SelectionContainer') {
    throw "Compose SelectionContainer import compatibility fix did not apply."
}
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($mainActivity, $content, $utf8NoBom)

Write-Host "Source archive verified, extracted, and Compose imports patched: $Destination"
