# 更新職缺（PRD 2.5 人工輸入流程）
# 1. 取得 data 分支最新版本  2. 分析 inbox\ 的職缺  3. 推送到 data 分支  4. 重新部署網站
# 本程式完全不連線 104；只連線 GitHub、Gemini 與證交所／櫃買中心公開資料。
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$env:PYTHONIOENCODING = 'utf-8'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Stop-WithMessage($msg) {
    Write-Host ""
    Write-Host $msg -ForegroundColor Red
    Read-Host "按 Enter 關閉"
    exit 1
}

$py = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { Stop-WithMessage "找不到 Python 虛擬環境（.venv）。請先依 README「本機開發」建立。" }
New-Item -ItemType Directory -Force (Join-Path $root 'inbox') | Out-Null

Write-Host "① 取得最新資料…" -ForegroundColor Cyan
if (-not (Test-Path (Join-Path $root 'data\.git'))) {
    $remote = git remote get-url origin
    git clone --quiet --branch data --single-branch $remote data
    if ($LASTEXITCODE -ne 0) { Stop-WithMessage "無法下載 data 分支，請確認網路與 GitHub 登入。" }
}
# Commits use the same identity as the main checkout (GitHub noreply address, PRD 11.2).
foreach ($k in 'user.name', 'user.email') {
    $v = git config $k
    if ($v) { git -C data config $k $v }
}
git -C data pull --quiet --ff-only
if ($LASTEXITCODE -ne 0) { Stop-WithMessage "data 分支更新失敗（可能有尚未推送的修改）。請把這個視窗的內容截圖給維護者。" }

Write-Host "② 分析收件匣裡的職缺…" -ForegroundColor Cyan
& $py -m pipeline manual --data-dir data --inbox inbox
$code = $LASTEXITCODE

if (git -C data status --porcelain) {
    Write-Host ""
    Write-Host "③ 推送到 GitHub…" -ForegroundColor Cyan
    git -C data add -A
    git -C data commit --quiet -m ("Manual update " + (Get-Date -Format 'yyyy-MM-dd'))
    git -C data push --quiet origin HEAD:data
    if ($LASTEXITCODE -ne 0) { Stop-WithMessage "推送失敗。資料已存在本機 data 資料夾，下次執行會再試一次。" }
    Write-Host "④ 重新部署網站…" -ForegroundColor Cyan
    gh workflow run deploy.yml --repo ((git remote get-url origin) -replace '^https://github.com/', '' -replace '\.git$', '')
    if ($LASTEXITCODE -ne 0) { Write-Host "（部署沒有啟動，可到 GitHub Actions 手動執行 deploy）" -ForegroundColor Yellow }
    else { Write-Host "完成！約 2–3 分鐘後網站會更新。" -ForegroundColor Green }
} else {
    Write-Host ""
    Write-Host "沒有新的資料需要上傳。" -ForegroundColor Green
}
if ($code -ne 0) { Write-Host "分析過程有錯誤，請把這個視窗的內容截圖給維護者。" -ForegroundColor Yellow }
Read-Host "按 Enter 關閉"
