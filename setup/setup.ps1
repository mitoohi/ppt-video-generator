# setup.ps1 — 一键安装口播视频生成所需依赖 (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  口播视频自动生成 - 环境安装" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    Write-Host "   下载: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 检查/安装 ffmpeg
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpegPath) {
    Write-Host ""
    Write-Host "安装 ffmpeg..." -ForegroundColor Yellow

    $wingetPath = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetPath) {
        winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
    } else {
        $chocoPath = Get-Command choco -ErrorAction SilentlyContinue
        if ($chocoPath) {
            choco install ffmpeg -y
        } else {
            Write-Host "❌ 请手动安装 ffmpeg:" -ForegroundColor Red
            Write-Host "   方式1: winget install Gyan.FFmpeg" -ForegroundColor Yellow
            Write-Host "   方式2: 从 https://ffmpeg.org/download.html 下载并加入 PATH" -ForegroundColor Yellow
            exit 1
        }
    }

    # 刷新 PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ ffmpeg 已安装但可能需要重启终端才能使用" -ForegroundColor Yellow
}

# 安装 Python 依赖
Write-Host ""
Write-Host "安装 Python 依赖..." -ForegroundColor Yellow
pip install --upgrade pip
pip install edge-tts playwright mutagen Pillow

# 安装 Playwright 浏览器
Write-Host ""
Write-Host "安装 Playwright Chromium..." -ForegroundColor Yellow
python -m playwright install chromium

# 验证
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  验证安装" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

python -c @"
import edge_tts
import playwright
import mutagen
print('✓ edge-tts')
print('✓ playwright')
print('✓ mutagen')
"@

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  ✓ 安装完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "现在可以使用口播视频生成 SKILL 了。" -ForegroundColor White
Write-Host "在 Claude Code 中输入: 做一期 XX 主题的口播视频" -ForegroundColor White
