# create_video.py
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip

def create_video(image_path="image.jpg", audio_path="audio.mp3", output_path="final_video.mp4"):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path).set_duration(audio_clip.duration).resize(height=1920).set_position("center")
    video = CompositeVideoClip([image_clip]).set_audio(audio_clip)
    video.write_videofile(output_path, fps=24)
    print(f"Video created at {output_path}")

if __name__ == "__main__":
    create_video()
