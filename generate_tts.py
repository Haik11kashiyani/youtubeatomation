import os
import time
import requests

ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY1")
VOICE_ID = "H6QPv2pQZDcGqLwDTIJQ"

def generate_tts(text, output_path="audio.mp3", retries=3, delay=5):
    print("🎤 Generating audio from ElevenLabs...")

    for attempt in range(1, retries + 1):
        for model in ["eleven_multilingual_v2", "eleven_monolingual_v1"]:
            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
                headers={
                    "xi-api-key": ELEVENLABS_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": model,
                    "voice_settings": {
                        "stability": 0.6,
                        "similarity_boost": 0.8
                    }
                }
            )

            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Audio saved to {output_path} using model {model}")
                return output_path
            else:
                print(f"⚠️ Attempt {attempt}, model {model} failed: {response.status_code}, {response.text}")

        if attempt < retries:
            print(f"🔄 Retrying in {delay} seconds...")
            time.sleep(delay)

    raise RuntimeError("❌ All attempts failed to generate audio.")

if __name__ == "__main__":
    sample_text = "Hello world, this is a test."
    generate_tts(sample_text)
