import os
import requests

# Multiple API keys for failover
ELEVENLABS_KEYS = [
    os.getenv("ELEVENLABS_KEY1"),
    os.getenv("ELEVENLABS_KEY2"),
    os.getenv("ELEVENLABS_KEY3"),
]

SCRIPT_FILE = "video_meta.txt"  # auto-generated meta file
OUTPUT_FILE = "voiceover.mp3"

# Default voice ID (Rachel)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

def extract_script_from_meta():
    """Extracts only the Script text from video_meta.txt"""
    if not os.path.exists(SCRIPT_FILE):
        raise FileNotFoundError(f"❌ Script file not found: {SCRIPT_FILE}")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if "Script:" in content:
        script_text = content.split("Script:")[1].strip()
    else:
        script_text = content.strip()

    if not script_text:
        raise ValueError("❌ No script text found in video_meta.txt")

    return script_text

def generate_tts():
    script_text = extract_script_from_meta()
    print(f"🎤 Generating TTS for script: {script_text[:100]}...")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"Content-Type": "application/json"}
    data = {
        "text": script_text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    # Try each key until success
    for key in ELEVENLABS_KEYS:
        if not key:
            continue
        headers["xi-api-key"] = key
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                with open(OUTPUT_FILE, "wb") as f:
                    f.write(response.content)
                print(f"✅ Saved TTS audio using key ending with ...{key[-4:]} → {OUTPUT_FILE}")
                return
            else:
                print(f"⚠️ Key ...{key[-4:]} failed: {response.text}")
        except Exception as e:
            print(f"⚠️ Error with key ...{key[-4:]}: {e}")

    raise RuntimeError("❌ All ElevenLabs keys failed for TTS generation")

if __name__ == "__main__":
    generate_tts()
