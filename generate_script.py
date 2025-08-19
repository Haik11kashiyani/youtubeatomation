# generate_script.py
import random

# Example topics
daily_topics = ["Daily Horoscope", "Monthly Horoscope", "Yearly Horoscope", "Numerology Tips", "Astrology Lesson"]

def generate_script():
    topic = random.choice(daily_topics)
    # Bilingual example
    script_en = f"Today's {topic} for you is full of positive energy and opportunities."
    script_hi = f"आज का {topic} आपके लिए सकारात्मक ऊर्जा और अवसरों से भरा है।"
    return f"{script_en}\n{script_hi}", topic

if __name__ == "__main__":
    script, topic = generate_script()
    with open("script.txt", "w", encoding="utf-8") as f:
        f.write(script)
    print(f"Generated script for topic: {topic}")
