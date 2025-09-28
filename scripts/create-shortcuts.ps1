#requires -version 5
# Create handy desktop shortcuts (.lnk) for common locations & tools.
$desktop = [Environment]::GetFolderPath("Desktop")
$wsh = New-Object -ComObject WScript.Shell
function New-Shortcut($name, $target, $args="") {
  $lnk = $wsh.CreateShortcut((Join-Path $desktop "$name.lnk"))
  $lnk.TargetPath = $target; if ($args) { $lnk.Arguments = $args }; $lnk.Save()
  Write-Host "  + $name"
}
New-Shortcut "God Mode" "explorer.exe" "shell:::{ED7BA470-8E54-465E-825C-99712043E01C}"
New-Shortcut "Startup Folder" "explorer.exe" "shell:startup"
New-Shortcut "Apps Folder" "explorer.exe" "shell:AppsFolder"
New-Shortcut "Services" "services.msc"
New-Shortcut "Device Manager" "devmgmt.msc"
New-Shortcut "Disk Management" "diskmgmt.msc"
New-Shortcut "Task Manager" "taskmgr.exe"
New-Shortcut "Windows Update" "ms-settings:windowsupdate"
Write-Host "Shortcuts created on Desktop." -ForegroundColor Green
