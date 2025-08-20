# generate_tts.py
import os
import requests

# Get API key from GitHub Actions secret
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_KEY1")  # change to KEY2/KEY3 if needed

# Text to convert to speech
TEXT = "Welcome to your automated astrology short. Let's get started."

# Output file path (must match create_video.py)
OUTPUT_PATH = "audio.mp3"

def generate_tts():
    if not ELEVENLABS_API_KEY:
        raise ValueError("❌ ELEVENLABS_KEY1 is missing! Did you add it in GitHub Secrets?")

    # ElevenLabs TTS API
    url = "https://api.elevenlabs.io/v1/text-to-speech/exAVfXMRZp7w4D9Byu1Q"  # replace with your Voice ID
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    data = {
        "text": TEXT,
        "model_id": "eleven_multilingual_v2"
    }

    print("🎙️ Requesting TTS from ElevenLabs...")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"❌ TTS request failed: {response.status_code} {response.text}")

    # Save audio file
    with open(OUTPUT_PATH, "wb") as f:
        f.write(response.content)

    print(f"✅ Audio file saved as {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_tts()
