# generate_tts.py
import os
import requests

ELEVEN_KEYS = [
    os.getenv("ELEVENLABS_KEY1"),
    os.getenv("ELEVENLABS_KEY2"),
    os.getenv("ELEVENLABS_KEY3")
]

def get_script():
    with open("script.txt", "r", encoding="utf-8") as f:
        return f.read()

def generate_tts(output_file="audio.mp3"):
    script = get_script()
    key = ELEVEN_KEYS[0]  # Can rotate keys if needed
    url = "https://api.elevenlabs.io/v1/text-to-speech"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json"
    }
    data = {
        "voice": "your_preferred_voice_id",
        "input": script
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"TTS saved to {output_file}")
    else:
        print("TTS request failed:", response.text)

if __name__ == "__main__":
    generate_tts()
