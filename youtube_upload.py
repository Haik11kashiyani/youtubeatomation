"""
Automated YouTube Shorts Uploader
- Uploads all 12 rashifal videos from outputs folder
- Reads data from rashifal_data.json
- Auto-generates SMART titles with date, highlights, and hashtags
- Adds proper titles, tags, and descriptions
"""
import os
import json
import re
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
def read_rashifal_json(json_path: str) -> tuple:
    """Read rashifal data from JSON file and return rashis list and date."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["rashifal"], data.get("date", "")


# ==================== SMART TITLE GENERATOR ====================
def generate_smart_title(rashi_data: Dict, date: str) -> str:
    """
    Generate smart YouTube title with:
    - Rashi name
    - દૈનિક રાશિફળ
    - Short date (DD/MM)
    - Key highlight from content
    - #shorts #viral
    
    Max length: 100 characters
    """
    
    # Extract rashi name (e.g., "મેષ રાશિ" from "મેષ રાશિ (Aries) - દૈનિક રાશિફળ - 12/10/2025")
    title = rashi_data.get("TITLE", "")
    if "(" in title:
        rashi_name = title.split("(")[0].strip()
    else:
        rashi_name = title.split("-")[0].strip()
    
    # Format date (12/10/2025 -> 12/10)
    short_date = date.split("/")[0] + "/" + date.split("/")[1] if "/" in date else date
    
    # Extract key highlights from content
    content = rashi_data.get("content", {})
    highlight = extract_key_highlight(content)
    
    # Build title parts
    base = f"{rashi_name} દૈનિક રાશિફળ {short_date}"
    hashtags = " #shorts #viral"
    
    # Calculate remaining space for highlight
    remaining_space = 100 - len(base) - len(hashtags) - 3  # -3 for " | "
    
    if remaining_space > 15:  # Only add highlight if there's enough space
        # Trim highlight to fit
        if len(highlight) > remaining_space:
            highlight = highlight[:remaining_space-3] + "..."
        
        final_title = f"{base} | {highlight}{hashtags}"
    else:
        # If not enough space, skip highlight
        final_title = f"{base}{hashtags}"
    
    # Ensure it's under 100 chars
    return final_title[:100]


def extract_key_highlight(content: Dict[str, str]) -> str:
    """
    Extract the most important/exciting phrase from content.
    Looks for keywords like: લાભ, સફળતા, યોગ, નફો, પ્રેમ, નાણાં, etc.
    """
    
    # Priority keywords to look for (in order of importance)
    priority_keywords = [
        "ધન લાભ", "નફો", "સફળતા", "પ્રમોશન", "યોગ", 
        "પ્રેમ", "નાણાં", "ઉત્સાહ", "ખુશી", "શુભ", 
        "નવું", "આનંદ", "વિજય", "મજબૂત"
    ]
    
    # Search through content sections
    for section_text in content.values():
        # Clean text (remove extra spaces and newlines)
        clean_text = " ".join(section_text.split())
        
        # Look for priority keywords
        for keyword in priority_keywords:
            if keyword in clean_text:
                # Extract sentence containing keyword
                sentences = re.split('[.!?।\n]', clean_text)
                for sentence in sentences:
                    if keyword in sentence:
                        # Clean and trim sentence
                        highlight = sentence.strip()
                        # Remove common prefixes
                        highlight = highlight.replace("આજે ", "")
                        highlight = highlight.replace("તમારા માટે ", "")
                        highlight = highlight.replace("તમે ", "")
                        return highlight[:50]  # Max 50 chars for highlight
    
    # Fallback: use first 40 chars of first content section
    first_section = list(content.values())[0] if content else ""
    return " ".join(first_section.split())[:40]


# ==================== DESCRIPTION GENERATOR ====================
def generate_description(rashi_data: Dict, date: str) -> str:
    """Generate YouTube description from rashifal data."""
    
    title = rashi_data.get("TITLE", "")
    content = rashi_data.get("content", {})
    
    # Extract rashi name
    rashi_name = title.split("(")[0].strip() if "(" in title else title.split("-")[0].strip()
    
    # Build description
    description_parts = []
    
    # Header
    description_parts.append(f"🌟 {rashi_name} - દૈનિક રાશિફળ 🌟")
    description_parts.append(f"📅 તારીખ: {date}\n")
    
    # Add first 3 content sections as preview
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
    description_parts.append("🔔 વધુ દૈનિક રાશિફળ માટે સબ્સ્ક્રાઈબ કરો!")
    description_parts.append("💬 કોમેન્ટમાં તમારી રાશિ જણાવો!\n")
    
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
        "#Gujarat",
        "#Shorts",
        "#Viral"
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
    print(f"   Title: {title}")
    
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
                "horoscope shorts",
                "viral shorts",
                "gujarati astrology"
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
            try:
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
            except Exception as e:
                print(f"   ⚠️ Could not add to playlist: {e}")
        
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
    Reads titles and content from JSON to generate smart titles and descriptions.
    """
    
    print("\n" + "="*70)
    print("📤 YOUTUBE SHORTS AUTO UPLOADER")
    print("   Smart titles with date, highlights, and #shorts #viral")
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
        rashifal_list, date = read_rashifal_json(JSON_PATH)
        print(f"\n✅ Date from JSON: {date}")
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
    
    print(f"✅ Found {len(video_files)} videos to upload")
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
        
        # Generate SMART title and description
        smart_title = generate_smart_title(rashi_data, date)
        description = generate_description(rashi_data, date)
        
        print(f"\n{'='*70}")
        print(f"🎬 Processing: {video_filename}")
        print(f"   Generated Title: {smart_title}")
        print(f"   Length: {len(smart_title)} chars")
        
        # Upload
        video_id = upload_video(
            file_path=video_path,
            title=smart_title,
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
