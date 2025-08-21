import os
import requests
import random

# Get Hugging Face API key
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Horoscope signs
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def generate_with_huggingface(prompt):
    """Generate text using Hugging Face Inference API"""
    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",  # free model
            headers=headers,
            json={"inputs": prompt, "max_length": 150}
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        else:
            print("⚠️ Hugging Face response error:", data)
            return None
    except Exception as e:
        print("⚠️ Hugging Face error:", e)
        return None


def generate_script():
    """Generate horoscope script for a random zodiac sign"""
    sign = random.choice(SIGNS)
    prompt = f"Write a short daily horoscope for {sign}."

    if HUGGINGFACE_API_KEY:
        text = generate_with_huggingface(prompt)
        if text:
            script = f"♈ Daily Horoscope for {sign}:\n{text}"
        else:
            script = f"♈ Horoscope for {sign}: Stars are aligned for opportunities today."
    else:
        raise RuntimeError("❌ No API available. Please add at least Hugging Face API key.")

    # Save script
    with open("script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    print("✅ Script generated and saved to script.txt")


if __name__ == "__main__":
    generate_script()
