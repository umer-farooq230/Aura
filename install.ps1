# aura installer for Windows (PowerShell):
#   irm https://raw.githubusercontent.com/umer-farooq230/aura/main/install.ps1 | iex
$ErrorActionPreference = "Stop"

$Repo = if ($env:AURA_REPO) { $env:AURA_REPO } else { "umer-farooq230/aura" }
$Dest = Join-Path $env:LOCALAPPDATA "aura"
$Url  = "https://github.com/$Repo/releases/latest/download/aura-windows-x64.exe"

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Write-Host "Downloading aura ..."
Invoke-WebRequest -Uri $Url -OutFile (Join-Path $Dest "aura.exe")

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (($UserPath -split ";") -notcontains $Dest) {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$Dest", "User")
    Write-Host "Added $Dest to your PATH."
}
Write-Host "Done! Open a NEW terminal and try:  aura --list"
