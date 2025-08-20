import os
import requests
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def download_background():
    url = "https://picsum.photos/1080/1920"  # free random background image
    path = "background.png"
    if not os.path.exists(path):
        print("🌄 Downloading background image...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            print("✅ Background image downloaded.")
        else:
            raise RuntimeError(f"❌ Failed to download background image: {response.status_code}")
    return path

def create_video():
    # ensure background exists
    image_path = download_background()

    audio_path = "output.mp3"
    video_path = "final_video.mp4"

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"❌ Audio file not found: {audio_path}")

    print("🎬 Creating video...")

    # load assets
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path).set_duration(audio_clip.duration)

    # match size & add audio
    video_clip = image_clip.set_audio(audio_clip).resize(height=1920, width=1080)

    # export final video
    video_clip.write_videofile(video_path, fps=24)

    print(f"✅ Video created successfully: {video_path}")

if __name__ == "__main__":
    create_video()
