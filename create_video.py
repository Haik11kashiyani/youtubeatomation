# create_video.py
import os
import re
import random
import requests
from datetime import datetime
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
from bs4 import BeautifulSoup

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
VIDEO_OUTPUT = "final_video.mp4"

# -----------------------------------
# 1. Daily Horoscope & Numerology Fetcher
# -----------------------------------
def fetch_daily_horoscope(sign="leo"):
    """Fetch daily horoscope from an online source"""
    url = f"https://www.astroyogi.com/horoscopes/daily/{sign}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    para = soup.find("p")
    if para:
        return para.text.strip()
    return f"✨ Today brings new opportunities for {sign.title()}!"

def fetch_daily_numerology(number=7):
    """Fetch daily numerology prediction"""
    url = f"https://www.astroyogi.com/numerology/daily/{number}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    para = soup.find("p")
    if para:
        return para.text.strip()
    return f"🔮 Number {number} brings energy and transformation today!"

# -----------------------------------
# 2. Background Selector from Script
# -----------------------------------
def get_query_from_script(script_text: str) -> str:
    script_lower = script_text.lower()
    zodiac_signs = [
        "aries","taurus","gemini","cancer","leo","virgo",
        "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
    ]
    for sign in zodiac_signs:
        if sign in script_lower:
            return f"zodiac {sign}"
    if "number" in script_lower or "numerology" in script_lower:
        digits = [ch for ch in script_lower if ch.isdigit()]
        if digits:
            return f"numerology number {digits[0]}"
        return "numerology"
    if "horoscope" in script_lower:
        return "horoscope zodiac"
    return "astrology stars planets"

def download_background(query, save_path="background.png"):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=10"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ Pexels API error: {response.text}")
    data = response.json()
    if not data.get("photos"):
        raise FileNotFoundError(f"❌ No image found for query: {query}")
    photo = random.choice(data["photos"])
    img_url = photo["src"]["large"]
    img_data = requests.get(img_url).content
    with open(save_path, "wb") as f:
        f.write(img_data)
    print(f"✅ Downloaded background for '{query}'")
    return save_path

# -----------------------------------
# 3. Auto Tags & Hashtags Generator
# -----------------------------------
def generate_tags_and_hashtags(script_text):
    tags = []
    hashtags = []

    zodiac_signs = [
        "aries","taurus","gemini","cancer","leo","virgo",
        "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
    ]
    for sign in zodiac_signs:
        if sign in script_text.lower():
            tags.append(sign.title())
            hashtags.append(f"#{sign.title()}Horoscope")

    if "numerology" in script_text.lower():
        num_match = re.findall(r"\d+", script_text)
        if num_match:
            tags.append(f"Numerology {num_match[0]}")
            hashtags.append(f"#Numerology{num_match[0]}")
        hashtags.append("#Numerology")

    hashtags += ["#Horoscope", "#Astrology", "#Zodiac", "#DailyHoroscope"]
    return tags, " ".join(set(hashtags))

# -----------------------------------
# 4. Video Generator
# -----------------------------------
def create_video(script_text="Your Daily Horoscope ✨"):
    # Background
    query = get_query_from_script(script_text)
    bg_path = download_background(query)
    background = ImageClip(bg_path).set_duration(15).resize((1080, 1920))

    # Text overlay
    text = TextClip(
        script_text,
        fontsize=70,
        color="white",
        font="Arial-Bold",
        method="caption",
        size=(1000, None)
    ).set_duration(15).set_position("center")

    # Final composite
    final = CompositeVideoClip([background, text])
    final.write_videofile(VIDEO_OUTPUT, fps=30)
    print("✅ Video created:", VIDEO_OUTPUT)

# -----------------------------------
# 5. Main Automation
# -----------------------------------
if __name__ == "__main__":
    # Pick random mode: horoscope or numerology
    mode = random.choice(["horoscope", "numerology"])

    if mode == "horoscope":
        sign = random.choice([
            "aries","taurus","gemini","cancer","leo","virgo",
            "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
        ])
        script_text = f"♈ {sign.title()} Horoscope Today:\n{fetch_daily_horoscope(sign)}"
        title = f"✨ {sign.title()} Horoscope Today | {datetime.now().strftime('%B %d, %Y')}"
    else:
        number = random.randint(1, 9)
        script_text = f"🔮 Numerology {number}:\n{fetch_daily_numerology(number)}"
        title = f"🔢 Numerology {number} Prediction | {datetime.now().strftime('%B %d, %Y')}"

    # Generate tags + hashtags
    tags, hashtags = generate_tags_and_hashtags(script_text)
    description = f"{script_text}\n\n{hashtags}\n\n#DailyAstrology #Shorts"

    # Save everything for YouTube upload step
    with open("video_meta.txt", "w", encoding="utf-8") as f:
        f.write(f"{title}\n{description}\n{','.join(tags)}")

    print("🎬 Script:", script_text)
    print("🏷️ Title:", title)
    print("📌 Tags:", tags)
    print("📄 Description:", description)

    # Create video
    create_video(script_text)
