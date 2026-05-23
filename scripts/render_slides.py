"""
render_slides.py — 将 slides.json 渲染为 PNG 序列

依赖：playwright (pip install playwright && playwright install chromium)

用法：
    python render_slides.py <project_dir>

    project_dir 下需要有 slides.json，输出到 project_dir/ppt/images/
"""

import asyncio
import json
import sys
from pathlib import Path

WIDTH = 1920
HEIGHT = 1080
TEMPLATE_BASE = Path(__file__).parent.parent / "ppt" / "templates"


def resolve_template_dir(template_name: str) -> Path:
    d = TEMPLATE_BASE / template_name
    if not d.exists():
        raise FileNotFoundError(f"模板目录不存在: {d}")
    return d


def build_html(slide: dict, template_dir: Path, slide_index: int, total_slides: int) -> str:
    slide_type = slide.get("type", "content")
    template_file = template_dir / f"{slide_type}.html"
    if not template_file.exists():
        template_file = template_dir / "content.html"

    html = template_file.read_text(encoding="utf-8")

    replacements = {
        "{{title}}": slide.get("title", ""),
        "{{subtitle}}": slide.get("subtitle", ""),
        "{{text}}": slide.get("text", ""),
        "{{source}}": slide.get("source", ""),
        "{{slide_number}}": f"{slide_index:02d} / {total_slides:02d}",
        "{{id_num}}": str(slide_index),
        "{{id_large}}": str(slide_index),
        "{{id_tag}}": f"#{slide_index:02d}",
        "{{total}}": str(total_slides),
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    bullets = slide.get("bullets", [])
    bullets_html = "\n".join(f"      <li>{b}</li>" for b in bullets) if bullets else ""
    html = html.replace("{{bullets}}", bullets_html)

    table_data = slide.get("table")
    if table_data:
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])
        table_html = "<table>\n  <thead><tr>"
        table_html += "".join(f"<th>{h}</th>" for h in headers)
        table_html += "</tr></thead>\n  <tbody>"
        for row in rows:
            table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        table_html += "</tbody>\n</table>"
    else:
        table_html = ""
    html = html.replace("{{table}}", table_html)

    css_file = template_dir / "base.css"
    if css_file.exists():
        css_content = css_file.read_text(encoding="utf-8")
        html = html.replace(
            '<link rel="stylesheet" href="base.css">',
            f"<style>{css_content}</style>"
        )

    return html


async def render_all(project_dir: Path):
    slides_json = project_dir / "slides.json"
    if not slides_json.exists():
        print(f"错误: 找不到 {slides_json}")
        sys.exit(1)

    data = json.loads(slides_json.read_text(encoding="utf-8"))
    template_name = data.get("template", "modern-minimal")
    template_dir = resolve_template_dir(template_name)
    slides = data.get("slides", [])

    output_dir = project_dir / "ppt" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": WIDTH, "height": HEIGHT})
        page = await context.new_page()

        for idx, slide in enumerate(slides, start=1):
            slide_id = slide["id"]
            html_content = build_html(slide, template_dir, idx, len(slides))

            html_file = project_dir / "ppt" / f"slide-{slide_id:03d}.html"
            html_file.write_text(html_content, encoding="utf-8")

            # 用 file:// 加载，networkidle 等字体下载完
            try:
                await page.goto(html_file.resolve().as_uri(), wait_until="networkidle", timeout=30000)
            except Exception:
                # 网络异常时降级：仍可基于系统中文字体渲染
                await page.set_content(html_content, wait_until="domcontentloaded")

            # 显式等待 Web 字体就绪，避免中文方块
            try:
                await page.evaluate("document.fonts && document.fonts.ready")
            except Exception:
                pass
            await page.wait_for_timeout(400)

            screenshot_path = output_dir / f"slide-{slide_id:03d}.png"
            await page.screenshot(path=str(screenshot_path), full_page=False)
            print(f"  OK slide-{slide_id:03d}.png")

        await context.close()
        await browser.close()

    print(f"\n完成: {len(slides)} 页已渲染到 {output_dir}")


def main():
    if len(sys.argv) < 2:
        print("用法: python render_slides.py <project_dir>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    asyncio.run(render_all(project_dir))


if __name__ == "__main__":
    main()
