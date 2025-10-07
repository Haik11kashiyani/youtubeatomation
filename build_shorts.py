import os
import re
from typing import List, Dict, Optional, Tuple

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


def build_text_clip(text: str, fontsize: int, color: str, font_path: str, stroke_color: Optional[str] = None, stroke_width: int = 0, method: str = "caption", size: Optional[Tuple[int, int]] = None):
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


def compose_short(block: Dict[str, str]):
    title_text = block.get("YOUTUBE_SHORT_TITLE") or block.get("TITLE") or ""
    content_text = block.get("CONTENT", "")
    image_file = block.get("IMAGE", "")
    bg_music_hint = block.get("BG_MUSIC", "")

    # Base white background
    bg = ColorClip(size=(WIDTH, HEIGHT), color=(255, 255, 255)).set_duration(DURATION)

    # Rashi image at the top with fade in
    img_path = find_image_path(image_file)
    if img_path:
        img_clip = ImageClip(img_path).set_duration(DURATION)
        # Fit width with preserved aspect ratio, occupy top area (approx 40% height max)
        target_width = WIDTH - 160
        img_clip = img_clip.resize(width=target_width)
        # Position top centered with some margin
        top_margin = 60
        img_clip = img_clip.set_position(("center", top_margin)).fadein(0.6)
    else:
        img_clip = None

    # Title bold Gujarati, under image, always visible
    title_box_width = WIDTH - 160
    title_clip = build_text_clip(
        text=title_text,
        fontsize=64,
        color="black",
        font_path=GUJ_FONT_BOLD,
        method="caption",
        size=(title_box_width, None),
    ).set_duration(DURATION).set_position(("center", 560)).fadein(0.6)

    # Content segments change over time
    segments = split_content_to_segments(content_text, DURATION)
    # Allocate time evenly with small fade cross
    fade = 0.4
    seg_duration = max(2.5, (DURATION - fade * (len(segments) + 1)) / max(1, len(segments)))

    content_clips = []
    y_start = 720
    content_box_width = WIDTH - 200
    t = fade
    for seg in segments:
        c = build_text_clip(
            text=seg,
            fontsize=48,
            color="black",
            font_path=GUJ_FONT_REGULAR,
            method="caption",
            size=(content_box_width, None),
        ).set_duration(seg_duration).set_start(t).set_position(("center", y_start)).fadein(fade)
        content_clips.append(c)
        t += seg_duration

    # Compose layers
    layers = [bg]
    if img_clip is not None:
        layers.append(img_clip)
    layers.append(title_clip)
    layers.extend(content_clips)

    composite = CompositeVideoClip(layers, size=(WIDTH, HEIGHT)).set_duration(DURATION)

    # Audio: optional background music file name under assets if exists
    music_path = None
    if bg_music_hint:
        # try direct file name in assets
        hint_candidate = os.path.join(ASSETS_DIR, bg_music_hint)
        if os.path.exists(hint_candidate):
            music_path = hint_candidate
    # also support a default music.mp3 in assets
    if music_path is None:
        default_music = os.path.join(ASSETS_DIR, "music.mp3")
        if os.path.exists(default_music):
            music_path = default_music

    if music_path:
        try:
            music = AudioFileClip(music_path).volumex(0.25)
            if music.duration < DURATION:
                # loop music to fill
                loops = int(DURATION // music.duration) + 1
                music = AudioFileClip(music_path).fx(lambda clip: clip)
                # simple loop by concatenating not used; set_audio supports shorter - moviepy will cut
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


