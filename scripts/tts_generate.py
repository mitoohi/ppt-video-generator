"""
tts_generate.py — 根据 slides.json 批量生成口播音频 + 近似词级时间戳

edge-tts 7.x 不再输出 WordBoundary，改用 SentenceBoundary。
本脚本用 SubMaker 获取句子级时间戳，再将句子按"标点"切分为子句组
（不在子句内部强切，确保字幕不会把完整短句切成两半），
按字数比例分配每个子句在原句内的相对时间。

依赖：edge-tts (pip install edge-tts)

用法：
    python tts_generate.py <project_dir>
"""

import asyncio
import json
import sys
import re
from pathlib import Path

MAX_RETRIES = 3
# 标点切分集：中英混合
_PUNCT_PATTERN = re.compile(r'([，。！？；：、,.!?])')


def split_text_into_groups(text: str) -> list[str]:
    """按标点切分子句；绝不在子句内部强切。

    规则：
      - 仅在 ，。！？；：、 和英文 ,.!? 处切分
      - 标点保留在前一段末尾
      - 没有标点的长句保持完整一段
    """
    if not text or not text.strip():
        return []

    parts = _PUNCT_PATTERN.split(text)
    groups: list[str] = []
    buffer = ""

    for part in parts:
        if part is None or part == "":
            continue
        if _PUNCT_PATTERN.fullmatch(part):
            buffer += part
            seg = buffer.strip()
            if seg:
                groups.append(seg)
            buffer = ""
        else:
            buffer += part

    tail = buffer.strip()
    if tail:
        groups.append(tail)

    return groups if groups else [text.strip()]


def distribute_timeline(sentence_offset: float, sentence_duration: float, text: str) -> list[dict]:
    """将句子级时间戳按字数比例分配给标点切分后的子句组。"""
    groups = split_text_into_groups(text)
    if not groups:
        return []

    total_chars = sum(len(g) for g in groups)
    if total_chars == 0:
        return []

    result = []
    current_offset = sentence_offset

    for g in groups:
        char_ratio = len(g) / total_chars
        duration = sentence_duration * char_ratio
        result.append({
            "text": g,
            "offset": round(current_offset, 3),
            "duration": round(duration, 3),
        })
        current_offset += duration

    return result


async def generate_edge_tts(text: str, output_path: str, voice: str, rate: str):
    """生成音频并返回近似的子句级时间戳（每条对应一个标点段）。"""
    import edge_tts

    word_timings = []

    for attempt in range(MAX_RETRIES):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            submaker = edge_tts.SubMaker()

            with open(output_path, "wb") as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] == "SentenceBoundary":
                        submaker.feed(chunk)

            srt_content = submaker.get_srt()
            sentence_timings = parse_srt(srt_content)

            for st in sentence_timings:
                groups = distribute_timeline(st["offset"], st["duration"], st["text"])
                word_timings.extend(groups)

            return word_timings

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    重试 ({attempt + 1}/{MAX_RETRIES}): {e}")
                await asyncio.sleep(2)
            else:
                raise RuntimeError(f"TTS 生成失败 ({output_path}): {e}")


def parse_srt(srt_content: str) -> list[dict]:
    """Parse simple SRT content into {text, offset, duration}"""
    entries = []
    for block in srt_content.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        time_line = lines[1]
        text = " ".join(lines[2:])

        parts = time_line.split(" --> ")
        if len(parts) != 2:
            continue

        start = _srt_time_to_seconds(parts[0])
        end = _srt_time_to_seconds(parts[1])

        entries.append({
            "text": text,
            "offset": start,
            "duration": end - start,
        })

    return entries


def _srt_time_to_seconds(t: str) -> float:
    h, m, s_ms = t.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


async def generate_all(project_dir: Path):
    slides_json = project_dir / "slides.json"
    if not slides_json.exists():
        print(f"错误: 找不到 {slides_json}")
        sys.exit(1)

    data = json.loads(slides_json.read_text(encoding="utf-8"))
    voice = data.get("voice", "zh-CN-XiaoxiaoNeural")
    rate = data.get("rate", "+0%")
    slides = data.get("slides", [])

    audio_dir = project_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    all_timings = {}

    for slide in slides:
        slide_id = slide["id"]
        narration = slide.get("narration", "")
        if not narration.strip():
            print(f"  -- slide-{slide_id:03d} (无口播文本，跳过)")
            continue

        output_path = audio_dir / f"slide-{slide_id:03d}.mp3"
        word_timings = await generate_edge_tts(narration, str(output_path), voice, rate)
        all_timings[str(slide_id)] = {
            "narration": narration,
            "word_timings": word_timings
        }
        print(f"  OK slide-{slide_id:03d}.mp3 ({len(word_timings)} 段)")

    timings_path = project_dir / "word_timings.json"
    timings_path.write_text(json.dumps(all_timings, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n完成: 音频已生成到 {audio_dir}")
    print(f"      字幕时间戳已保存到 {timings_path}")


def main():
    if len(sys.argv) < 2:
        print("用法: python tts_generate.py <project_dir>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    asyncio.run(generate_all(project_dir))


if __name__ == "__main__":
    main()
