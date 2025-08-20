import os
import random
import requests
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

SCRIPT_FILE = "script.txt"
AUDIO_FILE = "output.mp3"
VIDEO_FILE = "final_video.mp4"

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_URL = "https://api.pexels.com/v1/search"

def fetch_images(query, limit=5):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": limit, "orientation": "portrait"}
    r = requests.get(PEXELS_URL, headers=headers, params=params)
    data = r.json()
    return [photo["src"]["large"] for photo in data.get("photos", [])]

def download_image(url, filename):
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)

def create_video():
    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError("❌ No audio file found")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read().lower()

    # Choose search query based on script
    if "horoscope" in script_text or any(z in script_text for z in ["aries","leo","zodiac","pisces"]):
        query = "zodiac astrology"
    else:
        query = "numerology numbers"

    images = fetch_images(query, limit=5)
    if not images:
        raise ValueError("❌ No images fetched from Pexels")

    clips = []
    for i, img_url in enumerate(images):
        img_file = f"bg_{i}.jpg"
        download_image(img_url, img_file)
        clip = ImageClip(img_file).set_duration(5)  # each image 5s
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")

    audio = AudioFileClip(AUDIO_FILE)
    final_clip = final_clip.set_audio(audio).set_duration(audio.duration)

    final_clip.write_videofile(VIDEO_FILE, fps=24)

if __name__ == "__main__":
    create_video()
