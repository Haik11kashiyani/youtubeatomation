"""
Automated YouTube Shorts Uploader
- Uploads all 12 rashifal videos from outputs folder
- Reads data from rashifal_data.json
- Auto-generates descriptions with rashifal info
- Adds proper titles, tags, and hashtags
"""
import os
import json
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Scopes for YouTube upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
JSON_PATH = os.path.join(BASE_DIR, "rashifal_data.json")

# ==================== YOUTUBE SERVICE ====================
def get_youtube_service():
    """Create YouTube API service with OAuth credentials."""
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


# ==================== DATA READING ====================
def read_rashifal_json(json_path: str) -> List[Dict]:
    """Read rashifal data from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["rashifal"]


# ==================== DESCRIPTION GENERATOR ====================
def generate_description(rashi_data: Dict) -> str:
    """Generate YouTube description from rashifal data."""
    
    title = rashi_data.get("TITLE", "")
    content = rashi_data.get("content", {})
    date = rashi_data.get("date", "")
    
    # Extract rashi name
    rashi_name = title.split("(")[0].strip() if "(" in title else title.split("-")[0].strip()
    
    # Build description
    description_parts = []
    
    # Header
    description_parts.append(f"🌟 {rashi_name} 🌟")
    description_parts.append(f"તારીખ: {date}\n")
    
    # Add first 2-3 content sections as preview
    preview_count = 0
    for heading, text in content.items():
        if preview_count >= 3:
            break
        description_parts.append(f"✨ {heading}:")
        # Limit text length for description
        preview_text = text[:150] + "..." if len(text) > 150 else text
        description_parts.append(f"{preview_text}\n")
        preview_count += 1
    
    # Call to action
    description_parts.append("\n📱 આ વિડિયો ગમે તો લાઈક અને શેર કરો!")
    description_parts.append("🔔 વધુ દૈનિક રાશિફળ માટે સબ્સ્ક્રાઈબ કરો!\n")
    
    # Hashtags
    hashtags = [
        "#GujaratiRashifal",
        "#DailyHoroscope",
        "#Rashifal",
        "#Astrology",
        "#GujaratiShorts",
        "#Horoscope",
        f"#{rashi_name.replace(' ', '')}",
        "#Zodiac",
        "#Gujarat"
    ]
    description_parts.append(" ".join(hashtags))
    
    return "\n".join(description_parts)


# ==================== VIDEO UPLOAD ====================
def upload_video(
    file_path: str,
    title: str,
    description: str,
    tags: List[str] = None,
    playlist_id: str = None
):
    """Upload a single video to YouTube."""
    
    print(f"\n📤 Uploading: {os.path.basename(file_path)}")
    print(f"   Title: {title[:60]}...")
    
    try:
        service = get_youtube_service()
        
        # Prepare media file
        media = MediaFileUpload(
            file_path,
            chunksize=-1,
            resumable=True,
            mimetype="video/*"
        )
        
        # Default tags if none provided
        if tags is None:
            tags = [
                "gujarati rashifal",
                "daily horoscope",
                "astrology",
                "zodiac",
                "rashifal",
                "gujarati",
                "horoscope shorts"
            ]
        
        # Prepare request body
        body = {
            "snippet": {
                "title": title[:100],  # YouTube limit: 100 chars
                "description": description[:5000],  # YouTube limit: 5000 chars
                "tags": tags[:500],  # YouTube limit: 500 tags
                "categoryId": "24"  # Entertainment category
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        # Upload request
        request = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        # Execute upload with progress
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"      Upload progress: {progress}%", end="\r")
        
        print(f"\n   ✅ Upload complete!")
        print(f"   🎬 Video ID: {response['id']}")
        print(f"   🔗 URL: https://youtube.com/shorts/{response['id']}")
        
        # Add to playlist if specified
        if playlist_id:
            service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": response["id"]
                        }
                    }
                }
            ).execute()
            print(f"   ✅ Added to playlist: {playlist_id}")
        
        return response["id"]
        
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ==================== MAIN UPLOAD FUNCTION ====================
def upload_all_rashifal_videos(playlist_id: str = None):
    """
    Upload all rashifal videos from outputs folder.
    Reads titles and content from JSON to generate descriptions.
    """
    
    print("\n" + "="*70)
    print("📤 YOUTUBE SHORTS AUTO UPLOADER")
    print("   Uploading all rashifal videos with auto-generated descriptions")
    print("="*70)
    
    # Check JSON file
    if not os.path.exists(JSON_PATH):
        print(f"\n❌ ERROR: JSON file not found: {JSON_PATH}")
        return
    
    # Check outputs directory
    if not os.path.exists(OUTPUTS_DIR):
        print(f"\n❌ ERROR: Outputs directory not found: {OUTPUTS_DIR}")
        print("   Run build_shorts.py first to create videos!")
        return
    
    # Read rashifal data
    try:
        rashifal_list = read_rashifal_json(JSON_PATH)
    except Exception as e:
        print(f"\n❌ JSON Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Get all video files from outputs
    video_files = [f for f in os.listdir(OUTPUTS_DIR) if f.endswith('.mp4')]
    
    if not video_files:
        print(f"\n❌ No video files found in: {OUTPUTS_DIR}")
        print("   Run build_shorts.py first!")
        return
    
    print(f"\n✅ Found {len(video_files)} videos to upload")
    print(f"✅ Found {len(rashifal_list)} rashis in JSON\n")
    
    # Match videos with rashifal data
    uploaded_count = 0
    failed_count = 0
    
    for rashi_data in rashifal_list:
        video_filename = rashi_data.get("OUTPUT_FILENAME")
        
        if not video_filename:
            print(f"⚠️ Skipping: No OUTPUT_FILENAME in JSON")
            continue
        
        video_path = os.path.join(OUTPUTS_DIR, video_filename)
        
        if not os.path.exists(video_path):
            print(f"⚠️ Video not found: {video_filename}")
            failed_count += 1
            continue
        
        # Generate title and description
        youtube_title = rashi_data.get("YOUTUBE_SHORT_TITLE", rashi_data.get("TITLE", ""))
        description = generate_description(rashi_data)
        
        # Upload
        video_id = upload_video(
            file_path=video_path,
            title=youtube_title,
            description=description,
            playlist_id=playlist_id
        )
        
        if video_id:
            uploaded_count += 1
        else:
            failed_count += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"✅ UPLOAD COMPLETE!")
    print(f"   ✅ Uploaded: {uploaded_count}/{len(rashifal_list)}")
    print(f"   ❌ Failed: {failed_count}")
    print("="*70 + "\n")


# ==================== MAIN ====================
if __name__ == "__main__":
    # Optional: Get playlist ID from environment or hardcode
    playlist_id = os.getenv("YOUTUBE_PLAYLIST_ID", None)
    
    # Upload all videos
    upload_all_rashifal_videos(playlist_id=playlist_id)