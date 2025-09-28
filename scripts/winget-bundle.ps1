#requires -version 5
# Essential Windows toolset via winget. Edit the list to taste.
$ErrorActionPreference = "Continue"
$pkgs = @(
  "7zip.7zip", "voidtools.Everything", "CodeSector.TeraCopy", "Microsoft.PowerToys",
  "Microsoft.Sysinternals", "Notepad++.Notepad++", "Microsoft.WindowsTerminal",
  "ShareX.ShareX", "Rufus.Rufus", "Ventoy.Ventoy", "RevoUninstaller.RevoUninstaller",
  "Klocman.BulkCrapUninstaller", "REALiX.HWiNFO", "WinDirStat.WinDirStat",
  "Tailscale.Tailscale", "WiresharkFoundation.Wireshark", "Insecure.Nmap",
  "marticliment.UniGetUI", "Git.Git", "Python.Python.3.12"
)
foreach ($p in $pkgs) {
  Write-Host "Installing $p ..." -ForegroundColor Cyan
  winget install --id $p -e --accept-source-agreements --accept-package-agreements
}
Write-Host "Done. See TOOLS.md for tools not on winget (Hiren's, Win10Privacy, MAS)." -ForegroundColor Green
