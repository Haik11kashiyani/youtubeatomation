import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"]

SCRIPT_FILE = "script.txt"
VIDEO_FILE = "final_video.mp4"

def get_youtube_service():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=SCOPES
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def detect_category(script_text: str) -> str:
    text = script_text.lower()
    horoscope_keywords = ["horoscope","zodiac","aries","taurus","leo","virgo","cancer","pisces","scorpio"]
    numerology_keywords = ["numerology","life path","destiny number","soul urge","birth number"]

    if any(word in text for word in horoscope_keywords):
        return "horoscope"
    elif any(word in text for word in numerology_keywords):
        return "numerology"
    else:
        return "horoscope"  # fallback default

def upload_video(file_path=VIDEO_FILE, title=None, description=None, tags=None, playlist_id=None):
    service = get_youtube_service()
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/*")

    body = {
        "snippet": {
            "title": title or "Astrology Shorts 🌌",
            "description": description or "Daily astrology update",
            "tags": tags or ["astrology","shorts","zodiac","numerology"]
        },
        "status": {"privacyStatus": "public"}
    }

    request = service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status: 
            print(f"Upload {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"✅ Upload complete: https://youtu.be/{video_id}")

    if playlist_id:
        service.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id}
                }
            }
        ).execute()
        print(f"✅ Added to playlist {playlist_id}")

if __name__ == "__main__":
    # read script
    if not os.path.exists(SCRIPT_FILE):
        raise FileNotFoundError("❌ script.txt not found")
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read()

    # detect category
    category = detect_category(script_text)
    playlist_id = os.getenv("SERIES1_PLAYLIST_ID") if category=="horoscope" else os.getenv("SERIES2_PLAYLIST_ID")

    # generate dynamic title & description
    title = f"{category.title()} Shorts 🌌 - {script_text[:50]}..."
    description = script_text + "\n\n#shorts #astrology #viral"

    upload_video(
        file_path=VIDEO_FILE,
        title=title,
        description=description,
        playlist_id=playlist_id
    )
