import os
import requests

# Load API key from environment variables
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY1")

# Your selected voice ID
VOICE_ID = "H6QPv2pQZDcGqLwDTIJQ"

def generate_tts(text, output_path="audio.mp3"):
    print("🎤 Generating audio from ElevenLabs...")

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "model_id": "eleven_monolingual_v1",  # use "eleven_multilingual_v1" for multi-language
            "voice_settings": {
                "stability": 0.6,
                "similarity_boost": 0.8
            }
        }
    )

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Audio saved to {output_path}")
        return output_path
    else:
        raise RuntimeError(f"❌ Failed to generate audio: {response.status_code}, {response.text}")

if __name__ == "__main__":
    # Example text for testing
    sample_text = "Welcome to our Astrology Shorts! Stay tuned for daily predictions and insights."
    generate_tts(sample_text)
