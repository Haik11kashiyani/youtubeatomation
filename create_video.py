import os
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip

def create_video():
    # Always use the same folder as this script for audio/video
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_dir, "audio.mp3")
    image_path = os.path.join(base_dir, "background.png")
    output_path = os.path.join(base_dir, "final_video.mp4")

    # ✅ Check if audio exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"❌ Audio file not found: {audio_path}. Did generate_tts.py run successfully?")

    # ✅ Check if image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ Background image not found: {image_path}")

    # Load audio
    audio_clip = AudioFileClip(audio_path)

    # Load image and set duration to match audio
    image_clip = ImageClip(image_path).set_duration(audio_clip.duration)

    # Set audio to image
    final_clip = image_clip.set_audio(audio_clip)

    # Export video
    final_clip.write_videofile(output_path, fps=24)

    print(f"✅ Video created successfully at {output_path}")

if __name__ == "__main__":
    create_video()
