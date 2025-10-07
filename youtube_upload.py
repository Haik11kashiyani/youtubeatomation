# youtube_upload.py
import os
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

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

def read_blocks(script_path: str) -> List[Dict[str, str]]:
    """Parse script file into blocks separated by ###### lines."""
    import re
    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read()
    raw_blocks = re.split(r"\n#{6,}\n", text.strip())
    blocks: List[Dict[str, str]] = []
    for raw in raw_blocks:
        if not raw.strip():
            continue
        data: Dict[str, str] = {}
        lines = [l.rstrip("\n") for l in raw.splitlines()]
        for key in ["TITLE", "YOUTUBE_SHORT_TITLE", "OUTPUT_FILENAME"]:
            for ln in lines:
                if ln.startswith(f"{key}:"):
                    data[key] = ln.replace(f"{key}:", "").strip()
                    break
        blocks.append(data)
    return blocks

def upload_video(file_path="final_video.mp4", title: str = "Astrology Shorts", description: str = "Daily astrology", tags: List[str] | None = None, playlist_id: str | None = None):
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
        if status:
            print(f"Upload {int(status.progress() * 100)}%")
    print("✅ Upload complete.")

    if playlist_id:
        service.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": response["id"]}
                }
            }
        ).execute()
        print(f"✅ Added video to playlist {playlist_id}")


def upload_all_from_script(outputs_dir: str = "outputs", script_path: str = "script.txt"):
    blocks = read_blocks(script_path)
    for block in blocks:
        out_name = block.get("OUTPUT_FILENAME") or "final_video.mp4"
        title = block.get("YOUTUBE_SHORT_TITLE") or block.get("TITLE") or "Astrology Shorts"
        file_path = os.path.join(outputs_dir, out_name)
        if not os.path.exists(file_path):
            print(f"⚠️ Skipping missing file: {file_path}")
            continue
        upload_video(file_path=file_path, title=title)

if __name__ == "__main__":
    # Upload all rendered shorts in outputs using titles from script
    upload_all_from_script(outputs_dir="outputs", script_path="script.txt")
