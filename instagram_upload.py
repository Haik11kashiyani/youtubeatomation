# instagram_upload.py
from instagrapi import Client
import os

def upload_reel(video_path="final_video.mp4", caption="Daily Astrology"):
    cl = Client()
    cl.login(os.getenv("IG_USERNAME"), os.getenv("IG_PASSWORD"))
    cl.video_upload(video_path, caption=caption)
    print("Instagram Reel uploaded")

if __name__ == "__main__":
    try:
        upload_reel()
    except Exception as e:
        print("Instagram upload failed:", e)
