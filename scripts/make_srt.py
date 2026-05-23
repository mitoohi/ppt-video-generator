"""
make_srt.py — 从 timeline.json 生成 SRT 字幕

依赖：无（纯 Python 标准库）

用法：
    python make_srt.py <project_dir>

    读取 project_dir/timeline.json，输出 project_dir/subtitles.srt
"""

import json
import sys
from pathlib import Path


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(project_dir: Path):
    timeline_path = project_dir / "timeline.json"
    if not timeline_path.exists():
        print(f"错误: 找不到 {timeline_path}，请先运行 plan_timeline.py")
        sys.exit(1)

    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    subtitles = timeline.get("subtitles", [])

    if not subtitles:
        print("警告: timeline.json 中没有字幕数据")
        return

    entries = []
    for sub in subtitles:
        entries.append(
            f"{sub['index']}\n"
            f"{format_srt_time(sub['start'])} --> {format_srt_time(sub['end'])}\n"
            f"{sub['text']}\n"
        )

    srt_path = project_dir / "subtitles.srt"
    srt_path.write_text("\n".join(entries), encoding="utf-8")

    total_duration = subtitles[-1]["end"] if subtitles else 0
    print(f"OK subtitles.srt 已生成: {len(entries)} 条字幕, 覆盖 {total_duration:.1f}s")


def main():
    if len(sys.argv) < 2:
        print("用法: python make_srt.py <project_dir>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    generate_srt(project_dir)


if __name__ == "__main__":
    main()
