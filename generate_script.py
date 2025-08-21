import os
import requests
import datetime

# Get API keys from GitHub secrets (env variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

SCRIPT_FILE = "script.txt"


def fetch_trending_topics():
    """Simulate trending/real-world events (placeholder)"""
    today = datetime.datetime.now().strftime("%B %d, %Y")
    return f"Today is {today}, and people are talking about upcoming festivals, world events, and viral trends on social media."


def generate_with_openai(prompt):
    import openai
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a viral script generator for YouTube shorts."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI error: {e}")
        return None


def generate_with_gemini(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return None


def generate_with_huggingface(prompt):
    try:
        url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        r = requests.post(url, headers=headers, json={"inputs": prompt})
        data = r.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        elif isinstance(data, dict) and "error" in data:
            print("⚠️ Hugging Face error:", data["error"])
        return None
    except Exception as e:
        print(f"⚠️ Hugging Face error: {e}")
        return None


def generate_script():
    trending = fetch_trending_topics()

    prompt = f"""
Generate a short viral YouTube script in an engaging, human-like tone. 
Make it related to horoscopes, numerology, or motivation. 
Incorporate trending world events, upcoming festivals, or viral cultural themes.
End with strong engagement hooks (like "Follow for more", "Your sign will love this").
Also include 5-7 trending hashtags.

Trending context to include: {trending}
"""

    script_text = None

    if OPENAI_API_KEY:
        script_text = generate_with_openai(prompt)

    if not script_text and GEMINI_API_KEY:
        script_text = generate_with_gemini(prompt)

    if not script_text and HUGGINGFACE_API_KEY:
        script_text = generate_with_huggingface(prompt)

    if not script_text:
        raise RuntimeError("❌ No API available. Please add at least Hugging Face API key.")

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script_text)

    print(f"✅ Script saved to {SCRIPT_FILE}")


if __name__ == "__main__":
    generate_script()
