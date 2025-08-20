import os
import random
import moviepy.editor as mp


def pick_random_file(folder, extensions=("png", "jpg", "jpeg", "mp4")):
    """Pick a random asset file from a folder"""
    files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
    if not files:
        raise FileNotFoundError(f"No valid assets in {folder}")
    return os.path.join(folder, random.choice(files))


def detect_series_type(script_text):
    """Detect whether script is horoscope or numerology"""
    horoscope_keywords = ["aries", "taurus", "leo", "zodiac", "horoscope", "virgo", "capricorn", "scorpio"]
    numerology_keywords = ["life path", "number", "destiny", "numerology", "digit"]

    script_lower = script_text.lower()
    if any(word in script_lower for word in horoscope_keywords):
        return "horoscope"
    elif any(word in script_lower for word in numerology_keywords):
        return "numerology"
    else:
        return "horoscope"  # default fallback


def create_video():
    base_dir = os.path.dirname(__file__)
    assets_dir = os.path.join(base_dir, "assets")

    # 1. Load script to detect series
    script_file = os.path.join(base_dir, "script.txt")
    if not os.path.exists(script_file):
        raise FileNotFoundError("❌ script.txt not found!")
    with open(script_file, "r", encoding="utf-8") as f:
        script_text = f.read()

    series_type = detect_series_type(script_text)
    print(f"📌 Detected series type: {series_type}")

    series_dir = os.path.join(assets_dir, series_type)
    if not os.path.exists(series_dir):
        raise FileNotFoundError(f"❌ Missing assets folder: {series_dir}")

    # 2. Randomly select assets
    bg_path = pick_random_file(series_dir, ("png", "jpg", "jpeg", "mp4"))
    overlay_path = pick_random_file(series_dir, ("png", "jpg", "jpeg"))

    # 3. Audio
    audio_path = os.path.join(base_dir, "output.mp3")
    if not os.path.exists(audio_path):
        raise FileNotFoundError("❌ output.mp3 not found!")

    audio = mp.AudioFileClip(audio_path)

    # 4. Background (image or video)
    if bg_path.endswith(".mp4"):
        background = mp.VideoFileClip(bg_path).resize(height=1080).set_duration(audio.duration)
    else:
        background = mp.ImageClip(bg_path).set_duration(audio.duration).resize(height=1080)

    # 5. Overlay
    overlay = mp.ImageClip(overlay_path).set_duration(audio.duration).resize(height=1080).set_opacity(0.35)

    # 6. Composite final video
    video = mp.CompositeVideoClip([background, overlay]).set_audio(audio)

    # 7. Export
    output_path = os.path.join(base_dir, f"{series_type}_video.mp4")
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    print(f"✅ Video saved: {output_path}")


if __name__ == "__main__":
    create_video()
