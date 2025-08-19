# youtube_upload.py
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"]

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

def upload_video(file_path="final_video.mp4", title="Astrology Shorts", description="Daily astrology", tags=None, playlist_id=None):
    service = get_youtube_service()
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/*")
    body = {
        "snippet": {"title": title, "description": description, "tags": tags or []},
        "status": {"privacyStatus": "public"}
    }
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status: print(f"Upload {int(status.progress()*100)}%")
    print("Upload complete.")
    if playlist_id:
        service.playlistItems().insert(
            part="snippet",
            body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": response["id"]}}}
        ).execute()
        print(f"Added video to playlist {playlist_id}")

if __name__ == "__main__":
    upload_video(playlist_id=os.getenv("SERIES1_PLAYLIST_ID"))
