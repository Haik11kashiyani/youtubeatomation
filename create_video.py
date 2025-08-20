# create_video.py
import requests
import os
import random
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
VIDEO_OUTPUT = "final_video.mp4"

def get_query_from_script(script_text: str) -> str:
    """
    Detects a query for Pexels based on script content.
    Horoscope → zodiac sign, Numerology → numbers, Astrology → stars, etc.
    """
    script_lower = script_text.lower()

    zodiac_signs = [
        "aries","taurus","gemini","cancer","leo","virgo",
        "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
    ]

    # Check zodiac
    for sign in zodiac_signs:
        if sign in script_lower:
            return f"zodiac {sign}"

    # Numerology detection
    if "number" in script_lower or "numerology" in script_lower:
        # Extract a digit if possible
        digits = [ch for ch in script_lower if ch.isdigit()]
        if digits:
            return f"numerology number {digits[0]}"
        return "numerology"

    # Horoscope generic
    if "horoscope" in script_lower:
        return "horoscope zodiac"

    # Astrology fallback
    return "astrology stars planets"

def download_background(query, save_path="background.png"):
    """
    Downloads a background image from Pexels based on query.
    """
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=10"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ Pexels API error: {response.text}")

    data = response.json()
    if not data.get("photos"):
        raise FileNotFoundError(f"❌ No image found for query: {query}")

    # Pick one image (can randomize between top results)
    photo = random.choice(data["photos"])
    img_url = photo["src"]["large"]

    img_data = requests.get(img_url).content
    with open(save_path, "wb") as f:
        f.write(img_data)

    print(f"✅ Downloaded background for '{query}': {save_path}")
    return save_path

def create_video(script_text="Your Horoscope Today"):
    """
    Creates a vertical short video with background chosen based on script.
    """
    # 1. Pick query from script
    query = get_query_from_script(script_text)

    # 2. Download background
    bg_path = download_background(query)

    # 3. Load background
    background = ImageClip(bg_path).set_duration(15).resize((1080, 1920))

    # 4. Add text overlay
    text = TextClip(
        script_text,
        fontsize=70,
        color="white",
        font="Arial-Bold",
        method="caption",
        size=(1000, None)
    ).set_duration(15).set_position("center")

    # 5. Composite video
    final = CompositeVideoClip([background, text])

    # 6. Export
    final.write_videofile(VIDEO_OUTPUT, fps=30)
    print("✅ Video created:", VIDEO_OUTPUT)

if __name__ == "__main__":
    # Example usage
    create_video("♌ Leo Horoscope Today: Big changes are coming your way!")
