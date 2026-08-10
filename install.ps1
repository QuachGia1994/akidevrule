# akidevrule installer — thin PowerShell launcher for Windows.
# Resolves a Python 3 interpreter, then delegates all logic to install.py.

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot

$py = $null
foreach ($candidate in @("py", "python3", "python")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3") {
            $py = $candidate
            break
        }
    } catch {
        # candidate not found — try next
    }
}

if (-not $py) {
    Write-Error (
        "Python 3 not found. Install it from https://www.python.org/downloads/ " +
        "and ensure it is on your PATH, then re-run this script."
    )
    exit 1
}

& $py "$ScriptDir\install.py" @args
