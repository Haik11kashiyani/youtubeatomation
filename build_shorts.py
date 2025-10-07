import os
import re
from typing import List, Dict, Optional, Tuple
import difflib

from moviepy.editor import (
    ImageClip,
    ColorClip,
    CompositeVideoClip,
    TextClip,
    AudioFileClip,
)


BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "12 photos")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
SCRIPT_PATH = os.path.join(BASE_DIR, "script.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


WIDTH = 1080
HEIGHT = 1920
DURATION = 30.0
FPS = 30

GUJ_FONT_REGULAR = os.path.join(FONTS_DIR, "NotoSansGujarati-Regular.ttf")
GUJ_FONT_BOLD = os.path.join(FONTS_DIR, "NotoSansGujarati-Bold.ttf")


def read_script_blocks(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    raw_blocks = re.split(r"\n#{6,}\n", text.strip())
    blocks: List[Dict[str, str]] = []
    for raw in raw_blocks:
        if not raw.strip():
            continue
        data: Dict[str, str] = {}
        lines = [l.rstrip("\n") for l in raw.splitlines()]

        # Simple key extraction for first fields
        for key in ["TITLE", "IMAGE", "OUTPUT_FILENAME", "YOUTUBE_SHORT_TITLE", "BG_MUSIC"]:
            for ln in lines:
                if ln.startswith(f"{key}:"):
                    data[key] = ln.replace(f"{key}:", "").strip()
                    break

        # The content starts after a line ending with "RASHI ) :" marker or first blank after header fields
        content_start_idx = None
        for idx, ln in enumerate(lines):
            if ") :" in ln or ln.endswith(") :") or ln.endswith("):"):
                content_start_idx = idx + 1
                break
        if content_start_idx is None:
            # fallback: find first line that looks like bold section or paragraph after header keys
            header_count = sum(1 for k in ["TITLE", "IMAGE", "OUTPUT_FILENAME", "YOUTUBE_SHORT_TITLE", "BG_MUSIC"] if k in data)
            content_start_idx = min(len(lines), header_count + 1)

        content_lines = [l for l in lines[content_start_idx:] if l.strip()]
        data["CONTENT"] = "\n".join(content_lines).strip()

        blocks.append(data)

    return blocks


def find_image_path(filename: str) -> Optional[str]:
    if not filename:
        return None
    candidate = os.path.join(ASSETS_DIR, filename)
    return candidate if os.path.exists(candidate) else None


def build_text_clip(text: str, fontsize: int, color: str, font_path: str, stroke_color: Optional[str] = None, stroke_width: int = 0, method: str = "caption", size: Optional[Tuple[int, int]] = None, align: str = "center"):
    # MoviePy TextClip supports font by name when installed system-wide. We will use method="caption" with font set to the path via 'font' arg when possible.
    return TextClip(
        txt=text,
        fontsize=fontsize,
        color=color,
        font=font_path,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        method=method,
        size=size,
        align=align,
    )


def split_content_to_segments(content: str, total_duration: float, min_segment: float = 3.0, max_segment: float = 7.0) -> List[str]:
    # Split on double newlines or bullet-like paragraphs
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    if not paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", content)
        paragraphs = [s.strip() for s in sentences if s.strip()]
    if not paragraphs:
        return [content.strip()]

    # Fit number of segments to target total duration
    # Prefer 4-7 segments
    for target_segments in range(7, 2, -1):
        if len(paragraphs) >= target_segments:
            paragraphs = paragraphs[:target_segments]
            break

    return paragraphs


def _select_music_from_hint(hint: str) -> Optional[str]:
    if not hint:
        return None
    # Search audio files in ASSETS_DIR and fuzzy-match by filename
    try:
        candidates = []
        for name in os.listdir(ASSETS_DIR):
            if name.lower().endswith((".mp3", ".wav", ".m4a", ".ogg")):
                candidates.append(name)
        if not candidates:
            return None
        scores = [
            (difflib.SequenceMatcher(None, hint.lower(), c.lower()).ratio(), c)
            for c in candidates
        ]
        scores.sort(reverse=True)
        best = scores[0][1]
        return os.path.join(ASSETS_DIR, best)
    except Exception:
        return None

def _shorten(text: str, max_chars: int) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"

def _paginate_text(text: str, max_chars_per_page: int) -> List[str]:
    if not text:
        return [""]
    chunks: List[str] = []
    current: List[str] = []
    count = 0
    # Prefer splitting by lines/paragraphs
    units = [u.strip() for u in re.split(r"\n\s*\n|\n", text) if u.strip()]
    if not units:
        units = [text]
    for u in units:
        if count + len(u) + 1 <= max_chars_per_page:
            current.append(u)
            count += len(u) + 1
        else:
            if current:
                chunks.append("\n".join(current))
            # Very long single unit fallback: hard cut
            if len(u) > max_chars_per_page:
                for i in range(0, len(u), max_chars_per_page):
                    chunks.append(u[i:i + max_chars_per_page])
                current = []
                count = 0
            else:
                current = [u]
                count = len(u)
    if current:
        chunks.append("\n".join(current))
    return chunks or [text]


def compose_short(block: Dict[str, str]):
    # Use only TITLE on video per requirement
    title_text = block.get("TITLE") or ""
    content_text = block.get("CONTENT", "")
    image_file = block.get("IMAGE", "")
    bg_music_hint = block.get("BG_MUSIC", "")

    # Base white background
    bg = ColorClip(size=(WIDTH, HEIGHT), color=(255, 255, 255)).set_duration(DURATION)

    # Rashi image at the top
    img_path = find_image_path(image_file)
    img_intro_outro = []
    if img_path:
        base_img = ImageClip(img_path)
        target_width = WIDTH - 160
        base_img = base_img.resize(width=target_width).set_position(("center", 60))
        # Intro (0-2s)
        img_intro = base_img.set_start(0).set_duration(2.0).fadein(0.6).fadeout(0.6)
        # Outro (28-30s)
        img_outro = base_img.set_start(28.0).set_duration(2.0).fadein(0.6).fadeout(0.4)
        img_intro_outro = [img_intro, img_outro]

    # Title (intro/outro only)
    title_box_width = WIDTH - 160
    base_title = build_text_clip(
        text=title_text,
        fontsize=64,
        color="black",
        font_path=GUJ_FONT_BOLD,
        method="caption",
        size=(title_box_width, 220),
    ).set_position(("center", 560))
    title_intro = base_title.set_start(0).set_duration(2.0).fadein(0.6).fadeout(0.6)
    title_outro = base_title.set_start(28.0).set_duration(2.0).fadein(0.6).fadeout(0.4)

    # Split content into two 15-second parts
    # First, break content into paragraphs/sentences then distribute roughly half-half
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content_text) if p.strip()]
    if not paragraphs:
        sentences = re.split(r"(?<=[.!?\u0964\u0965])\s+", content_text)
        paragraphs = [s.strip() for s in sentences if s.strip()]
    if not paragraphs:
        paragraphs = [content_text.strip()]

    mid = max(1, len(paragraphs) // 2)
    part1_text = "\n\n".join(paragraphs[:mid])
    part2_text = "\n\n".join(paragraphs[mid:]) if len(paragraphs) > 1 else ""

    content_box_width = WIDTH - 200
    y_start = 720
    # Cap content length and box height to avoid ImageMagick caption size limits
    part1_pages = _paginate_text(part1_text, max_chars_per_page=280)
    part1_clips: List[TextClip] = []
    if not part1_pages:
        part1_pages = [""]
    per_page = max(3.0, 15.0 / len(part1_pages))
    t = 0.0
    for p in part1_pages:
        c = build_text_clip(
            text=p,
            fontsize=44,
            color="black",
            font_path=GUJ_FONT_REGULAR,
            method="caption",
            size=(content_box_width, 620),
            align="west",
        ).set_start(t).set_duration(per_page).set_position(("center", y_start)).fadein(0.4).fadeout(0.4)
        part1_clips.append(c)
        t += per_page

    second_text = part2_text or part1_text
    part2_pages = _paginate_text(second_text, max_chars_per_page=280)
    part2_clips: List[TextClip] = []
    if not part2_pages:
        part2_pages = [""]
    per_page2 = max(3.0, 15.0 / len(part2_pages))
    t = 15.0
    for p in part2_pages:
        c = build_text_clip(
            text=p,
            fontsize=44,
            color="black",
            font_path=GUJ_FONT_REGULAR,
            method="caption",
            size=(content_box_width, 620),
            align="west",
        ).set_start(t).set_duration(per_page2).set_position(("center", y_start)).fadein(0.4).fadeout(0.4)
        part2_clips.append(c)
        t += per_page2

    # Compose layers
    layers = [bg]
    layers.extend(img_intro_outro)
    layers.append(title_intro)
    layers.append(title_outro)
    layers.extend(part1_clips)
    layers.extend(part2_clips)

    composite = CompositeVideoClip(layers, size=(WIDTH, HEIGHT)).set_duration(DURATION)

    # Audio: choose by hint using fuzzy match, else default music.mp3
    music_path = None
    if bg_music_hint:
        music_path = _select_music_from_hint(bg_music_hint)
    if music_path is None:
        default_music = os.path.join(ASSETS_DIR, "music.mp3")
        if os.path.exists(default_music):
            music_path = default_music

    if music_path:
        try:
            music = AudioFileClip(music_path).volumex(0.25)
            composite = composite.set_audio(music.set_duration(DURATION))
        except Exception:
            pass

    return composite


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    ensure_output_dir()
    blocks = read_script_blocks(SCRIPT_PATH)
    for idx, block in enumerate(blocks):
        output_name = block.get("OUTPUT_FILENAME") or f"short_{idx+1}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        clip = compose_short(block)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=FPS)
        print(f"✅ Rendered: {output_path}")


if __name__ == "__main__":
    main()


