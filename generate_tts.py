import os
import requests
import time

# Collect all API keys from environment
keys = [
    os.getenv("ELEVENLABS_KEY1"),
    os.getenv("ELEVENLABS_KEY2"),
    os.getenv("ELEVENLABS_KEY3"),
]

VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Default ElevenLabs voice (you can change)
OUTPUT_FILE = "narration.mp3"

# Read the script that was generated
with open("script.txt", "r", encoding="utf-8") as f:
    text = f.read()


def generate_tts(api_key: str) -> bool:
    """
    Generate TTS audio with a given ElevenLabs API key.
    Returns True if successful, False otherwise.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.8},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Request failed for key {api_key[:6]}... : {e}")
        return False

    if response.status_code == 200:
        with open(OUTPUT_FILE, "wb") as f:
            f.write(response.content)
        print(f"✅ TTS generated successfully with key {api_key[:6]}...")
        return True
    else:
        print(f"❌ Failed with key {api_key[:6]}... : {response.text}")
        return False


# Try each key until one works
success = False
for key in keys:
    if key:
        print(f"🔑 Trying ElevenLabs key {key[:6]}...")
        if generate_tts(key):
            success = True
            break
        time.sleep(2)  # wait before trying next key

if not success:
    raise Exception("🚨 All ElevenLabs keys failed! Check your API keys or quota.")
