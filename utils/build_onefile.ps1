$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path "$ScriptDir\..\qtranslate.py") {
    $RootDir = Resolve-Path "$ScriptDir\.."
} else {
    $RootDir = Resolve-Path "."
}
Set-Location $RootDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [1/2] Checking resources and generating icons..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if (Test-Path "extension.png") {
    if (-not (Test-Path "extension.ico")) {
        Write-Host "Generating extension.ico from extension.png..." -ForegroundColor Yellow
        python -c "from PIL import Image; im = Image.open('extension.png'); im.save('extension.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
    }
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [2/2] Building single portable executable (Onefile) with Nuitka..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

python -m nuitka `
    --onefile `
    --windows-console-mode=disable `
    --enable-plugin=pyside6 `
    --include-package=ctranslate2 `
    --include-package=sentencepiece `
    --include-data-files=extension.png=extension.png `
    --nofollow-import-to=torch `
    --nofollow-import-to=spacy `
    --nofollow-import-to=stanza `
    --no-deployment-flag=excluded-module-usage `
    --windows-icon-from-ico=extension.png `
    --output-dir=dist `
    --output-filename=QuickTranslate.exe `
    qtranslate.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host " Portable executable successfully built!" -ForegroundColor Green
    Write-Host " Output: dist\QuickTranslate.exe" -ForegroundColor Green
    Write-Host " (This file does not require external folders or dependencies)" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
} else {
    Write-Error "Nuitka compilation failed!"
    exit $LASTEXITCODE
}
