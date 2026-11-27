# 在桌面建立兩個捷徑（只需執行一次）：「更新職缺」與「職缺收件匣」（PRD 2.5）
$root = Split-Path -Parent $PSScriptRoot
$inbox = Join-Path $root 'inbox'
New-Item -ItemType Directory -Force $inbox | Out-Null
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell

$s = $shell.CreateShortcut((Join-Path $desktop '更新職缺.lnk'))
$s.TargetPath = Join-Path $root 'tools\update-jobs.cmd'
$s.WorkingDirectory = $root
$s.Description = '分析收件匣裡的 104 職缺並更新網站'
$s.Save()

$s = $shell.CreateShortcut((Join-Path $desktop '職缺收件匣.lnk'))
$s.TargetPath = $inbox
$s.Description = '把 104 職缺頁面整頁貼成 .txt 放在這裡'
$s.Save()

Write-Host "已在桌面建立「更新職缺」與「職缺收件匣」。"
