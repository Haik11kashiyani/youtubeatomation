import os
import random
import requests
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# -------- CONFIG --------
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")  # Add to GitHub Secrets

ASSET_DIRS = {
    "zodiac": "assets/zodiac",
    "numerology": "assets/numerology",
    "backgrounds": "assets/backgrounds"
}

OUTPUT_VIDEO = "final_video.mp4"
AUDIO_FILE = "output.mp3"  # from generate_tts.py
SCRIPT_FILE = "script.txt" # contains horoscope/numerology text


# -------- HELPER FUNCTIONS --------
def ensure_folders():
    """Make sure all asset folders exist."""
    for folder in ASSET_DIRS.values():
        os.makedirs(folder, exist_ok=True)


def fetch_from_pexels(query, folder, count=5):
    """Fetch images from Pexels API and save them locally."""
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={count}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        for idx, img in enumerate(resp.json().get("photos", [])):
            img_url = img["src"]["large"]
            img_data = requests.get(img_url).content
            path = os.path.join(folder, f"{query}_{idx}.jpg")
            with open(path, "wb") as f:
                f.write(img_data)
            print(f"✅ Saved {path}")
    else:
        print("⚠️ Pexels fetch failed:", resp.text)


def get_assets_for_topic(topic, folder):
    """Get or fetch images for the given topic."""
    files = [f for f in os.listdir(folder) if f.endswith((".png", ".jpg", ".jpeg"))]
    if not files:  # Fetch fresh if empty
        print(f"📥 Fetching new assets for {topic}...")
        fetch_from_pexels(topic, folder)
        files = [f for f in os.listdir(folder) if f.endswith((".png", ".jpg", ".jpeg"))]
    return [os.path.join(folder, f) for f in files]


# -------- MAIN VIDEO CREATION --------
def create_video():
    ensure_folders()

    # Read script
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read().lower()

    # Detect type of content
    if "zodiac" in script_text or any(sign in script_text for sign in 
        ["aries","taurus","gemini","cancer","leo","virgo","libra","scorpio","sagittarius","capricorn","aquarius","pisces"]):
        topic = "zodiac"
    elif "number" in script_text or "numerology" in script_text:
        topic = "numerology"
    else:
        topic = "backgrounds"

    # Pick assets
    assets = get_assets_for_topic(topic, ASSET_DIRS[topic])
    chosen = random.sample(assets, min(3, len(assets)))

    # Load audio
    audio = AudioFileClip(AUDIO_FILE)

    # Create video from images
    clips = []
    duration_per_img = audio.duration / len(chosen)
    for img in chosen:
        clip = ImageClip(img).set_duration(duration_per_img)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile(OUTPUT_VIDEO, fps=24)


if __name__ == "__main__":
    create_video()
