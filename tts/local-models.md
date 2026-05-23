# 本地开源 TTS 备选方案

当 edge-tts 无法满足需求（离线环境、音色克隆、更高质量）时，可切换到以下本地方案。

## 方案对比

| 方案 | 中文质量 | GPU 需求 | 安装难度 | 特色 |
|---|---|---|---|---|
| CosyVoice2 | ★★★★★ | NVIDIA 6GB+ | 高 | 阿里开源，零样本克隆 |
| IndexTTS2 | ★★★★★ | NVIDIA 8GB+ | 高 | B站开源，工业级 |
| GPT-SoVITS | ★★★★ | NVIDIA 4GB+ | 中 | 少样本克隆友好 |
| ChatTTS | ★★★★ | NVIDIA 4GB+ | 中 | 对话感强 |
| Piper | ★★ | 不需要 | 低 | 纯 CPU，但中文音色少 |

---

## CosyVoice2（推荐）

### 安装

```bash
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice
pip install -r requirements.txt

# 下载模型权重（约 2GB）
python -c "from cosyvoice.cli.cosyvoice import CosyVoice; CosyVoice('pretrained_models/CosyVoice2-0.5B')"
```

### 使用

```python
from cosyvoice.cli.cosyvoice import CosyVoice
import torchaudio

cosyvoice = CosyVoice('pretrained_models/CosyVoice2-0.5B')

# 预设音色
output = cosyvoice.inference_sft("大家好，今天我们来聊一个话题", "中文女")
torchaudio.save("output.wav", output["tts_speech"], 22050)

# 零样本克隆（提供 3-10 秒参考音频）
output = cosyvoice.inference_zero_shot(
    "要合成的文本",
    "参考音频中说的文字",
    load_audio("reference.wav")
)
```

### 集成到本项目

修改 `scripts/tts_generate.py` 中的 `TTS_BACKEND` 常量：

```python
TTS_BACKEND = "cosyvoice"  # 改为 "cosyvoice"
COSYVOICE_MODEL_PATH = "path/to/CosyVoice/pretrained_models/CosyVoice2-0.5B"
```

---

## IndexTTS2

### 安装

```bash
git clone https://github.com/bilibili/Index-TTS.git
cd Index-TTS
pip install -r requirements.txt
# 下载模型权重（见项目 README）
```

### 使用

```python
from indextts import IndexTTS

tts = IndexTTS(model_dir="checkpoints/indextts2")
tts.infer("大家好", "reference.wav", "output.wav")
```

---

## GPT-SoVITS

### 安装

```bash
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
pip install -r requirements.txt
# 下载预训练模型
```

### 使用

通过 WebUI 或 API 调用，详见项目文档。

---

## 适配接口

所有本地方案都需要实现以下接口，供 `tts_generate.py` 调用：

```python
async def generate_audio(text: str, output_path: str, voice: str, rate: str) -> None:
    """
    生成单条音频。
    
    Args:
        text: 口播文本
        output_path: 输出文件路径（.wav 或 .mp3）
        voice: 音色标识（本地方案中可能是模型路径或预设名）
        rate: 语速调整（本地方案中可能需要转换为具体参数）
    """
    ...
```

切换方案时只需修改 `tts_generate.py` 顶部的 `TTS_BACKEND` 常量和对应配置，无需改动其他脚本。
