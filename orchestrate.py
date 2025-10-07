import os
from typing import Dict

from build_shorts import (
    read_script_blocks,
    compose_short,
    OUTPUT_DIR,
    SCRIPT_PATH,
    FPS,
)
from youtube_upload import upload_video


def render_one(block: Dict[str, str]) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_name = block.get("OUTPUT_FILENAME") or "short.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_name)
    clip = compose_short(block)
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=FPS)
    return output_path


def main():
    blocks = read_script_blocks(SCRIPT_PATH)
    for idx, block in enumerate(blocks, start=1):
        title = block.get("YOUTUBE_SHORT_TITLE") or block.get("TITLE") or f"Short {idx}"
        print(f"\n=== Processing {idx}/{len(blocks)}: {title} ===")
        video_path = render_one(block)
        print(f"✅ Rendered: {video_path}")
        print("⬆️ Uploading...")
        upload_video(file_path=video_path, title=title)
        print(f"✅ Uploaded: {title}")


if __name__ == "__main__":
    main()


