$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path "$ScriptDir\..\qtranslate.py") {
    $RootDir = Resolve-Path "$ScriptDir\.."
} else {
    $RootDir = Resolve-Path "."
}
Set-Location $RootDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [1/3] Checking resources and generating icons..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if (Test-Path "extension.png") {
    if (-not (Test-Path "extension.ico")) {
        Write-Host "Generating extension.ico from extension.png..." -ForegroundColor Yellow
        python -c "from PIL import Image; im = Image.open('extension.png'); im.save('extension.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
    }
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [2/3] Building Standalone package with Nuitka..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

python -m nuitka `
    --standalone `
    --windows-console-mode=disable `
    --enable-plugin=pyside6 `
    --include-package=ctranslate2 `
    --include-package=sentencepiece `
    --nofollow-import-to=torch `
    --nofollow-import-to=spacy `
    --nofollow-import-to=stanza `
    --no-deployment-flag=excluded-module-usage `
    --windows-icon-from-ico=extension.png `
    --output-dir=dist `
    --output-filename=QuickTranslate.exe `
    qtranslate.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Nuitka compilation failed!"
    exit $LASTEXITCODE
}

if (Test-Path "extension.png") {
    Copy-Item "extension.png" "dist\qtranslate.dist\extension.png" -Force
}
if (Test-Path "extension.ico") {
    Copy-Item "extension.ico" "dist\qtranslate.dist\extension.ico" -Force
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [3/3] Packaging into installer with Inno Setup..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ISCC = $null
$CandidatePaths = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)

foreach ($Path in $CandidatePaths) {
    if ($Path -and (Test-Path $Path)) {
        $ISCC = $Path
        break
    }
}

if (-not $ISCC) {
    $cmd = Get-Command "iscc.exe" -ErrorAction SilentlyContinue
    if ($cmd) {
        $ISCC = $cmd.Source
    }
}

if (-not $ISCC) {
    Write-Host "Inno Setup not found. Installing via winget..." -ForegroundColor Yellow
    winget install --id JRSoftware.InnoSetup -e --accept-source-agreements --accept-package-agreements --silent
    foreach ($Path in $CandidatePaths) {
        if ($Path -and (Test-Path $Path)) {
            $ISCC = $Path
            break
        }
    }
}

if (-not $ISCC) {
    Write-Error "Failed to find ISCC.exe (Inno Setup Compiler). Please install Inno Setup 6."
    exit 1
}

Write-Host "Using compiler: $ISCC" -ForegroundColor Gray
& "$ISCC" "utils\installer.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host " Installer successfully built!" -ForegroundColor Green
    Write-Host " Output: dist\installer\QuickTranslate_Setup_v1.2.0.exe" -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
} else {
    Write-Error "Inno Setup compilation failed!"
    exit $LASTEXITCODE
}
