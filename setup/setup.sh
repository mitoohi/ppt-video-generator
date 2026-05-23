#!/usr/bin/env bash
# setup.sh — 一键安装口播视频生成所需依赖 (macOS / Linux)

set -e

echo "========================================="
echo "  口播视频自动生成 - 环境安装"
echo "========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.10+"
    echo "   macOS: brew install python"
    echo "   Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Python $PYTHON_VERSION"

# 安装 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "安装 ffmpeg..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ 请先安装 Homebrew: https://brew.sh"
            exit 1
        fi
    else
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y ffmpeg
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y ffmpeg
        else
            echo "❌ 请手动安装 ffmpeg"
            exit 1
        fi
    fi
fi
echo "✓ ffmpeg $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"

# 安装 Python 依赖
echo ""
echo "安装 Python 依赖..."
pip3 install --upgrade pip
pip3 install edge-tts playwright mutagen Pillow

# 安装 Playwright 浏览器
echo ""
echo "安装 Playwright Chromium..."
python3 -m playwright install chromium

# 验证
echo ""
echo "========================================="
echo "  验证安装"
echo "========================================="
python3 -c "
import edge_tts
import playwright
import mutagen
print('✓ edge-tts')
print('✓ playwright')
print('✓ mutagen')
"

echo ""
echo "========================================="
echo "  ✓ 安装完成！"
echo "========================================="
echo ""
echo "现在可以使用口播视频生成 SKILL 了。"
echo "在 Claude Code 中输入: 做一期 XX 主题的口播视频"
