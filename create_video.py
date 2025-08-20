import os
import random
import requests
import moviepy.editor as mp

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")  # add this in GitHub secrets


def fetch_assets(query, folder, limit=2):
    """Fetch random images from Pexels and save new ones"""
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={limit}&page={random.randint(1,50)}"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"⚠️ Failed to fetch assets for {query}")
        return

    data = r.json()
    os.makedirs(folder, exist_ok=True)

    for i, photo in enumerate(data.get("photos", [])):
        img_url = photo["src"]["large"]
        filename = f"{query}_{random.randint(1000,9999)}.jpg"
        out_path = os.path.join(folder, filename)
        with open(out_path, "wb") as f:
            f.write(requests.get(img_url).content)
        print(f"⬇️ Downloaded: {out_path}")


def pick_random_file(folder, extensions=("png", "jpg", "jpeg", "mp4")):
    files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
    if not files:
        return None
    return os.path.join(folder, random.choice(files))


def detect_series_type(script_text):
    horoscope_keywords = ["aries", "taurus", "leo", "zodiac", "horoscope", "virgo", "capricorn", "scorpio"]
    numerology_keywords = ["life path", "number", "destiny", "numerology", "digit"]

    text = script_text.lower()
    if any(word in text for word in horoscope_keywords):
        return "horoscope"
    elif any(word in text for word in numerology_keywords):
        return "numerology"
    return "horoscope"


def create_video():
    base_dir = os.path.dirname(__file__)
    cache_dir = os.path.join(base_dir, "assets", "cache")

    script_file = os.path.join(base_dir, "script.txt")
    if not os.path.exists(script_file):
        raise FileNotFoundError("❌ script.txt not found!")
    with open(script_file, "r", encoding="utf-8") as f:
        script_text = f.read()

    series_type = detect_series_type(script_text)
    print(f"📌 Detected series type: {series_type}")

    series_folder = os.path.join(cache_dir, series_type)
    os.makedirs(series_folder, exist_ok=True)

    # ✅ always refresh some new assets each run
    query = "zodiac astrology" if series_type == "horoscope" else "numerology numbers cosmic"
    fetch_assets(query, series_folder, limit=2)

    bg_path = pick_random_file(series_folder, ("png", "jpg", "jpeg", "mp4"))
    overlay_path = pick_random_file(series_folder, ("png", "jpg", "jpeg"))

    audio_path = os.path.join(base_dir, "output.mp3")
    if not os.path.exists(audio_path):
        raise FileNotFoundError("❌ output.mp3 not found!")

    audio = mp.AudioFileClip(audio_path)

    if bg_path.endswith(".mp4"):
        background = mp.VideoFileClip(bg_path).resize(height=1080).set_duration(audio.duration)
    else:
        background = mp.ImageClip(bg_path).set_duration(audio.duration).resize(height=1080)

    overlay = mp.ImageClip(overlay_path).set_duration(audio.duration).resize(height=1080).set_opacity(0.3)

    video = mp.CompositeVideoClip([background, overlay]).set_audio(audio)
    output_path = os.path.join(base_dir, f"{series_type}_video.mp4")
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    print(f"✅ Video saved: {output_path}")


if __name__ == "__main__":
    create_video()
