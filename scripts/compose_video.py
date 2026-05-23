"""
compose_video.py — 根据 timeline.json 将 PNG + 音频 + 字幕合成为 MP4

依赖：ffmpeg (系统 PATH 中可用)

用法：
    python compose_video.py <project_dir>

    读取 project_dir/timeline.json，输出 project_dir/final.mp4

设计原则：
    - timeline.json 是所有时间数据的唯一来源
    - 视频用 xfade 平滑过渡（仅画面）
    - 音频用 concat 直接拼接（无交叉淡化）
    - 最后补帧对齐音视频时长
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_ffmpeg(cmd: list[str], desc: str) -> None:
    """运行 ffmpeg；失败时把 stderr 完整打印出来便于排错。"""
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(f"\n[ERROR] ffmpeg 失败：{desc}")
        print("命令:", " ".join(cmd))
        print("--- stderr ---")
        print(proc.stderr[-4000:])
        sys.exit(1)


def escape_subtitles_path(srt_path: Path) -> str:
    r"""ffmpeg 的 subtitles filter 在不同平台需要不同的转义策略。

    Windows: 把 'C:\path\file.srt' 转为 'C\:/path/file.srt'
    其他平台: 保持原样。
    返回值会再被外层用单引号包裹，如果路径包含单引号或反斜杠，整体放进 filter
    时再用 ffmpeg 自身的转义规则。
    """
    p = str(srt_path.resolve())
    if os.name == "nt":
        p = p.replace("\\", "/").replace(":", r"\:")
    # 单引号转义为 \'
    p = p.replace("'", r"\'")
    return p


def _srt_time_to_ass(t: str) -> str:
    h, m, s_ms = t.split(":")
    s, ms = s_ms.split(",")
    cs = int(round(int(ms) / 10))
    if cs >= 100:
        cs = 99
    return f"{int(h)}:{int(m):02d}:{int(s):02d}.{cs:02d}"


def srt_to_ass_1080(srt_path: Path, ass_path: Path) -> None:
    """SRT -> ASS, explicit PlayRes 1920x1080.

    用 ASS 取代 SRT，所有 margin/字号都按 1080p 实际像素生效，
    避免 SRT 默认的虚拟 PlayResY=288 把 MarginV 放大成实际像素的 ~3.75 倍。
    """
    style = (
        "Style: Default,Microsoft YaHei,65,"
        "&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,"
        "0,0,0,0,100,100,0,0,"
        "3,7,0,2,120,120,150,1"
    )
    header_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        ("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
         "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
         "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
         "Alignment, MarginL, MarginR, MarginV, Encoding"),
        style,
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    events: list[str] = []
    raw = srt_path.read_text(encoding="utf-8").strip()
    for block in raw.split("\n\n"):
        lines = [ln for ln in block.strip().split("\n") if ln.strip()]
        if len(lines) < 3:
            continue
        time_line = lines[1]
        if " --> " not in time_line:
            continue
        text = " ".join(lines[2:]).replace("\n", r"\N")
        a, b = time_line.split(" --> ")
        start = _srt_time_to_ass(a.strip())
        end = _srt_time_to_ass(b.strip())
        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    out = "\n".join(header_lines) + "\n" + "\n".join(events) + "\n"
    ass_path.write_text(out, encoding="utf-8")


def compose(project_dir: Path):
    timeline_path = project_dir / "timeline.json"
    if not timeline_path.exists():
        print(f"错误: 找不到 {timeline_path}，请先运行 plan_timeline.py")
        sys.exit(1)

    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))

    meta = timeline["meta"]
    segments = timeline["segments"]
    fade = float(meta["fade_duration"])
    fps = int(meta["fps"])
    total_audio = float(meta["total_audio_duration"])

    # 仅保留同时具备 image + audio 的可合成片段，避免 xfade offset 错位
    usable = [s for s in segments if s.get("image") and s.get("audio")]
    skipped = len(segments) - len(usable)
    if skipped > 0:
        print(f"[!] 跳过 {skipped} 个不完整片段（缺图或缺音频）")
    if not usable:
        print("错误: 没有可合成的片段")
        sys.exit(1)

    srt_path = project_dir / "subtitles.srt"
    output_path = project_dir / "final.mp4"

    print(f"片段数: {len(usable)}, 转场: {fade}s, 音频总长: {total_audio:.1f}s")

    tmp_dir = Path(tempfile.mkdtemp(prefix="ppt_video_"))
    segment_files: list[Path] = []

    # Step 1: 每个 slide 渲染为独立视频片段（图片 + 音频）
    print("\n生成片段...")
    for seg in usable:
        seg_file = tmp_dir / f"seg-{seg['slide_id']:03d}.mp4"
        img = project_dir / seg["image"]
        audio = project_dir / seg["audio"]
        duration = float(seg["audio_duration"])

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(img),
            "-i", str(audio),
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-shortest",
            "-r", str(fps), str(seg_file),
        ]
        run_ffmpeg(cmd, f"生成 seg-{seg['slide_id']:03d}.mp4")
        segment_files.append(seg_file)
        print(f"  OK seg-{seg['slide_id']:03d}.mp4 ({duration:.1f}s)")

    # Step 2: xfade 拼接视频 + concat 拼接音频
    print("\n合成（xfade 视频 + concat 音频）...")
    no_sub_path = tmp_dir / "no_sub.mp4"

    if len(segment_files) == 1:
        shutil.copy2(segment_files[0], no_sub_path)
    else:
        inputs: list[str] = []
        for f in segment_files:
            inputs.extend(["-i", str(f)])

        # 视频链：xfade 逐对叠加
        # offset_i = sum(audio_duration[0..i-1]) - i * fade
        xfade_chain: list[str] = []
        prev_label = "0:v"
        cumulative = 0.0
        for i in range(1, len(usable)):
            cumulative += float(usable[i - 1]["audio_duration"])
            offset = cumulative - i * fade
            cur_out = f"v{i}" if i < len(usable) - 1 else "vout"
            xfade_chain.append(
                f"[{prev_label}][{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}[{cur_out}]"
            )
            prev_label = cur_out

        video_filter = ";".join(xfade_chain)

        # 补帧对齐
        total_video_duration = total_audio - (len(usable) - 1) * fade
        pad_duration = total_audio - total_video_duration
        if pad_duration > 0.05:
            video_filter += f";[vout]tpad=stop_mode=clone:stop_duration={pad_duration:.3f}[outv]"
            map_v = "[outv]"
        else:
            map_v = "[vout]"

        # 音频链：直接拼接
        audio_concat = "".join(f"[{i}:a]" for i in range(len(usable)))
        audio_filter = f"{audio_concat}concat=n={len(usable)}:v=0:a=1[outa]"

        filter_complex = video_filter + ";" + audio_filter

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", map_v, "-map", "[outa]",
            "-c:v", "libx264", "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            str(no_sub_path),
        ]
        run_ffmpeg(cmd, "xfade 拼接")

    # Step 3: 烧入硬字幕
    print("烧入字幕...")
    if srt_path.exists() and srt_path.stat().st_size > 0:
        # 把 SRT 转成显式 PlayResX/Y 的 ASS，所有 margin/字号都按 1080 像素算
        ass_path = tmp_dir / "subtitles.ass"
        srt_to_ass_1080(srt_path, ass_path)
        sub_arg = escape_subtitles_path(ass_path)
        vf = f"subtitles='{sub_arg}'"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(no_sub_path),
            "-vf", vf,
            "-c:a", "copy",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            str(output_path),
        ]
        run_ffmpeg(cmd, "烧入字幕")
    else:
        shutil.copy2(no_sub_path, output_path)

    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\n完成: {output_path}")
    print(f"  时长: {total_audio:.1f}s ({total_audio / 60:.1f}min)")
    print(f"  分辨率: 1920×1080")
    print(f"  页数: {len(usable)}")
    print(f"  转场: fade {fade}s × {max(len(usable) - 1, 0)}")


def main():
    if len(sys.argv) < 2:
        print("用法: python compose_video.py <project_dir>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    compose(project_dir)


if __name__ == "__main__":
    main()
