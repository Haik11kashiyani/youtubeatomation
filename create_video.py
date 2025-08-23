import os
import requests
import random
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

# Config
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
SCRIPT_FILE = "script.txt"
NARRATION_FILE = "narration.mp3"
OUTPUT_FILE = "final_video.mp4"

DOWNLOAD_DIR = "clips"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def split_sentences(text: str):
    """Basic sentence splitter (periods, ?, !)"""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def extract_keyword(sentence: str):
    """Pick a keyword from a sentence"""
    words = re.findall(r"\b[a-zA-Z]{5,}\b", sentence)
    return random.choice(words) if words else "astrology"


def search_pixabay(query: str, max_results=5):
    """Search Pixabay for videos matching query."""
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query}&per_page={max_results}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"❌ Pixabay search failed: {resp.text}")
        return []
    data = resp.json()
    return [hit["videos"]["medium"]["url"] for hit in data.get("hits", [])]


def download_video(url: str, filename: str):
    """Download a video from Pixabay."""
    try:
        resp = requests.get(url, stream=True)
        if resp.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
            return filename
        else:
            print(f"❌ Download failed: {url}")
            return None
    except Exception as e:
        print(f"⚠️ Error downloading {url}: {e}")
        return None


def build_video():
    # Load script sentences
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    sentences = split_sentences(text)

    # Load narration audio
    if not os.path.exists(NARRATION_FILE):
        raise FileNotFoundError("🚨 Narration file not found.")
    narration = AudioFileClip(NARRATION_FILE)
    narration_duration = narration.duration

    # Allocate duration per sentence
    per_sentence = narration_duration / len(sentences)
    clips = []

    for i, sentence in enumerate(sentences):
        keyword = extract_keyword(sentence)
        urls = search_pixabay(keyword, max_results=3)
        if not urls:
            continue

        video_url = random.choice(urls)
        filename = os.path.join(DOWNLOAD_DIR, f"{keyword}_{i}.mp4")
        if download_video(video_url, filename):
            try:
                clip = VideoFileClip(filename)
                # Cut or loop to fit per_sentence duration
                if clip.duration > per_sentence:
                    clip = clip.subclip(0, per_sentence)
                else:
                    # If clip is short, loop it
                    loops = int(per_sentence // clip.duration) + 1
                    clip = concatenate_videoclips([clip] * loops).subclip(0, per_sentence)
                clips.append(clip)
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")

    if not clips:
        raise Exception("🚨 No clips could be downloaded from Pixabay.")

    # Concatenate and sync with narration
    final_clip = concatenate_videoclips(clips, method="compose").set_audio(narration)

    # Export final video
    final_clip.write_videofile(OUTPUT_FILE, codec="libx264", audio_codec="aac", fps=24)
    print(f"🎬 Final video saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_video()
