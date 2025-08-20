import os
import requests

ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY1")  # from GitHub secrets
SCRIPT_FILE = "script.txt"
OUTPUT_FILE = "output.mp3"

# You can customize the voice ID (pick from your ElevenLabs account)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # default: "Rachel"

def generate_tts():
    if not ELEVENLABS_KEY:
        raise ValueError("❌ ELEVENLABS_KEY1 not found in environment variables")

    # Read script text
    if not os.path.exists(SCRIPT_FILE):
        raise FileNotFoundError(f"❌ Script file not found: {SCRIPT_FILE}")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        raise ValueError("❌ Script file is empty")

    print(f"🎤 Generating TTS for script: {text[:100]}...")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise RuntimeError(f"❌ TTS generation failed: {response.text}")

    with open(OUTPUT_FILE, "wb") as f:
        f.write(response.content)

    print(f"✅ Saved TTS audio: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_tts()
