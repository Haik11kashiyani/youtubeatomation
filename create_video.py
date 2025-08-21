import os
import requests
import random
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip

# Config
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
SCRIPT_FILE = "script.txt"
NARRATION_FILE = "narration.mp3"
OUTPUT_FILE = "final_video.mp4"

DOWNLOAD_DIR = "clips"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def clean_and_extract_keywords(text: str, max_keywords=6):
    """
    Extract meaningful keywords from text.
    - Removes stopwords and short words
    - Picks nouns / main content words if possible
    """
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        from nltk.tag import pos_tag

        nltk.download("punkt", quiet=True)
        nltk.download("averaged_perceptron_tagger", quiet=True)
        nltk.download("stopwords", quiet=True)

        words = word_tokenize(text)
        words = [w.lower() for w in words if w.isalpha()]
        stop_words = set(stopwords.words("english"))
        words = [w for w in words if w not in stop_words]

        # Extract only nouns
        tagged = pos_tag(words)
        nouns = [word for word, tag in tagged if tag.startswith("NN")]

        # Pick random sample of nouns
        keywords = random.sample(nouns, min(max_keywords, len(nouns)))
        return keywords if keywords else words[:max_keywords]

    except Exception:
        # Fallback: just pick long words
        words = re.findall(r"\b[a-zA-Z]{5,}\b", text)
        return random.sample(words, min(max_keywords, len(words)))


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
    # Read script text
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()

    # Extract better keywords
    keywords = clean_and_extract_keywords(script)
    print(f"🔍 Keywords for Pixabay search: {keywords}")

    clips = []

    for word in keywords:
        urls = search_pixabay(word, max_results=3)
        if not urls:
            continue

        video_url = random.choice(urls)
        filename = os.path.join(DOWNLOAD_DIR, f"{word}.mp4")
        if download_video(video_url, filename):
            try:
                clip = VideoFileClip(filename).subclip(0, 5)  # first 5s
                clips.append(clip)
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")

    if not clips:
        raise Exception("🚨 No clips could be downloaded from Pixabay.")

    # Concatenate clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Add narration
    if os.path.exists(NARRATION_FILE):
        narration = AudioFileClip(NARRATION_FILE)
        final_clip = final_clip.set_audio(narration)
    else:
        print("⚠️ Narration file not found. Exporting video without audio.")

    # Export final video
    final_clip.write_videofile(OUTPUT_FILE, codec="libx264", audio_codec="aac", fps=24)
    print(f"🎬 Final video saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_video()
