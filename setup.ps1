<#
.SYNOPSIS
  Cognis guided setup wizard — one-line bootstrap for Windows PowerShell.

.EXAMPLE
  ./setup.ps1                # launch the guided, numbered-menu wizard
  ./setup.ps1 --dry-run      # show every command, never run it
  ./setup.ps1 --manifest URL # point at a specific MANIFEST.json (path or http(s) URL)

.NOTES
  Stdlib-only Python — nothing to install. Finds the first available interpreter.
#>
$ErrorActionPreference = 'Stop'

$dir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$wizard = Join-Path $dir 'cognis_setup.py'

$py = $null
foreach ($c in @('python', 'py', 'python3')) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Source; break }
}
# Common fixed install location as a last resort.
if (-not $py -and (Test-Path 'C:\Python314\python.exe')) { $py = 'C:\Python314\python.exe' }

if (-not $py) {
    Write-Error 'Cognis setup needs Python 3 (stdlib only). Install Python and re-run ./setup.ps1'
    exit 1
}

& $py $wizard @args
exit $LASTEXITCODE
