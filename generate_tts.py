import os
import requests
import time

# Collect all API keys from environment variables
keys = [
    os.getenv("ELEVENLABS_KEY1"),
    os.getenv("ELEVENLABS_KEY2"),
    os.getenv("ELEVENLABS_KEY3"),
]

VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Default ElevenLabs voice ID (change if needed)
OUTPUT_FILE = "narration.mp3"
SCRIPT_FILE = "script.txt"


def read_script() -> str:
    """
    Reads script.txt and extracts only the SCRIPT section.
    """
    if not os.path.exists(SCRIPT_FILE):
        raise FileNotFoundError(f"🚨 Script file not found: {SCRIPT_FILE}")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    script_started = False
    script_lines = []

    for line in lines:
        if line.strip().startswith("SCRIPT:"):
            script_started = True
            # Get text after "SCRIPT:" on the same line
            content = line.replace("SCRIPT:", "").strip()
            if content:
                script_lines.append(content)
            continue
        if script_started:
            script_lines.append(line.strip())

    script_text = "\n".join(script_lines).strip()

    if not script_text:
        raise ValueError("🚨 SCRIPT section is empty in script.txt")

    return script_text


def generate_tts(api_key: str, text: str) -> bool:
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
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.8,
        },
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


if __name__ == "__main__":
    # Extract only SCRIPT section
    text = read_script()

    success = False
    for key in keys:
        if key:
            print(f"🔑 Trying ElevenLabs key {key[:6]}...")
            if generate_tts(key, text):
                success = True
                break
            time.sleep(2)  # Small delay before next attempt

    if not success:
        raise Exception("🚨 All ElevenLabs keys failed! Check your API keys or quota.")
