# 环境安装脚本

## Windows

运行 `setup.ps1`（PowerShell）。

## macOS / Linux

运行 `setup.sh`（Bash）。

## 安装内容

| 依赖 | 用途 | 安装方式 |
|---|---|---|
| Python ≥ 3.10 | 脚本运行环境 | 需用户预装 |
| ffmpeg | 视频合成 | winget / brew / apt |
| playwright | HTML 截图 | pip + playwright install |
| edge-tts | TTS 语音合成 | pip |
| mutagen | 读取 mp3 时长 | pip |

## 验证

安装完成后脚本会自动验证：
- `python --version`
- `ffmpeg -version`
- `python -c "import playwright; import edge_tts; import mutagen"`
