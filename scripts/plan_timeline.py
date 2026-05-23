"""
plan_timeline.py — 根据词级时间戳 + 实际 mp3 时长，生成统一时间线 timeline.json

本脚本是整个管线「音画同步」的基准。make_srt.py 和 compose_video.py
都必须从 timeline.json 读取时间线，不得各自计算时长。

字幕粒度：信任 tts_generate.py 已经按"标点"切好的子句段，不再做二次重切，
确保完整的一句话不会被腰斩。仅在子句过长（> MAX_SUBTITLE_CHARS）时给出告警。

依赖：ffprobe（系统 PATH 中可用）

用法：
    python plan_timeline.py <project_dir>
"""

import json
import subprocess
import sys
from pathlib import Path

# 一行字幕的字符上限（仅用于告警）；超过此长度建议改写口播
MAX_SUBTITLE_CHARS = 30


def get_audio_duration(audio_path: Path) -> float:
    """用 ffprobe 获取 mp3 的精确时长（毫秒级精度）"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True
    )
    s = result.stdout.strip()
    if not s:
        raise RuntimeError(f"ffprobe 无法读取时长: {audio_path}")
    return float(s)


def words_to_subtitles(words: list[dict]) -> list[dict]:
    """直接将 TTS 阶段已按标点切好的子句作为字幕段使用。

    每个 word 项已经是一个完整子句（带尾标点），不再二次切分；
    仅在子句过长时打印告警提示用户改写口播。
    """
    segments = []
    for w in words:
        text = (w.get("text") or "").strip()
        if not text:
            continue
        if len(text) > MAX_SUBTITLE_CHARS:
            print(f"  [!] 字幕段过长（{len(text)} 字），建议在口播中加标点：{text[:30]}...")
        segments.append({
            "text": text,
            "offset": float(w["offset"]),
            "duration": float(w["duration"]),
        })
    return segments


def build_timeline(project_dir: Path):
    timings_path = project_dir / "word_timings.json"
    slides_json = project_dir / "slides.json"
    audio_dir = project_dir / "audio"
    images_dir = project_dir / "ppt" / "images"

    if not timings_path.exists():
        print(f"错误: 找不到 {timings_path}，请先运行 tts_generate.py")
        sys.exit(1)
    if not slides_json.exists():
        print(f"错误: 找不到 {slides_json}")
        sys.exit(1)

    timings_data = json.loads(timings_path.read_text(encoding="utf-8"))
    _ = json.loads(slides_json.read_text(encoding="utf-8"))

    FADE_DURATION = 0.6
    FPS = 30

    segments = []
    all_subtitles = []
    sub_index = 1

    cumulative_audio = 0.0  # 音频累计时间（不受 xfade 影响）

    for slide_key in sorted(timings_data.keys(), key=int):
        slide_info = timings_data[slide_key]
        slide_id = int(slide_key)

        audio_path = audio_dir / f"slide-{slide_id:03d}.mp3"
        word_timings = slide_info.get("word_timings", [])

        if audio_path.exists():
            audio_duration = get_audio_duration(audio_path)
        elif word_timings:
            last = word_timings[-1]
            audio_duration = float(last["offset"]) + float(last["duration"])
        else:
            audio_duration = 3.0

        img_path = images_dir / f"slide-{slide_id:03d}.png"

        segments.append({
            "slide_id": slide_id,
            "image": str(img_path.relative_to(project_dir).as_posix()) if img_path.exists() else None,
            "audio": str(audio_path.relative_to(project_dir).as_posix()) if audio_path.exists() else None,
            "narration": slide_info.get("narration", ""),
            "audio_duration": round(audio_duration, 3),
            "audio_start": round(cumulative_audio, 3),
            "audio_end": round(cumulative_audio + audio_duration, 3),
        })

        if word_timings:
            subs = words_to_subtitles(word_timings)
            for sub in subs:
                all_subtitles.append({
                    "index": sub_index,
                    "text": sub["text"],
                    "start": round(cumulative_audio + sub["offset"], 3),
                    "end": round(cumulative_audio + sub["offset"] + sub["duration"], 3),
                    "duration": round(sub["duration"], 3),
                    "belongs_to_slide": slide_id,
                })
                sub_index += 1

        cumulative_audio += audio_duration

    total_audio_duration = cumulative_audio
    total_video_duration = total_audio_duration - (len(segments) - 1) * FADE_DURATION if len(segments) > 1 else total_audio_duration

    timeline = {
        "meta": {
            "fade_duration": FADE_DURATION,
            "fps": FPS,
            "total_audio_duration": round(total_audio_duration, 3),
            "total_video_duration": round(total_video_duration, 3),
            "segment_count": len(segments),
            "subtitle_count": len(all_subtitles),
            "resolution": {"width": 1920, "height": 1080},
        },
        "segments": segments,
        "subtitles": all_subtitles,
    }

    timeline_path = project_dir / "timeline.json"
    timeline_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK timeline.json 已生成")
    print(f"  片段数: {len(segments)}")
    print(f"  字幕条数: {len(all_subtitles)}")
    print(f"  音频总时长: {total_audio_duration:.1f}s")
    print(f"  视频总时长: {total_video_duration:.1f}s (扣除 {max(len(segments) - 1, 0)} 次 {FADE_DURATION}s 转场)")
    print(f"\n  每段时间线:")
    for seg in segments:
        print(f"    Slide {seg['slide_id']:02d}: 音频 [{seg['audio_start']:.1f}s → {seg['audio_end']:.1f}s] ({seg['audio_duration']:.1f}s)")


def main():
    if len(sys.argv) < 2:
        print("用法: python plan_timeline.py <project_dir>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    build_timeline(project_dir)


if __name__ == "__main__":
    main()
