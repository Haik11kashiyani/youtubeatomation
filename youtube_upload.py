"""
Automated YouTube Shorts Uploader - 4 BATCHES VERSION
- Uploads rashifal videos in 4 batches (3 videos each)
- Batch 1: Rashis 1-3 (12 AM)
- Batch 2: Rashis 4-6 (2 AM)
- Batch 3: Rashis 7-9 (4 AM)
- Batch 4: Rashis 10-12 (6 AM)
- Reads data from rashifal_data.json
- Auto-generates smart titles with date and highlights
"""
import os
import json
import sys
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
    
    # Handle new structure with rashifal_dates array
    if "rashifal_dates" in data:
        # Get the first date's data
        first_date_data = data["rashifal_dates"][0]
        return first_date_data["rashifal"], first_date_data.get("date", "")
    else:
        # Old structure
        return data["rashifal"], data.get("date", "")


# ==================== SMART TITLE GENERATOR ====================
def generate_smart_title(rashi_data: Dict, date: str) -> str:
    """Generate smart YouTube title with date, highlights, and hashtags."""
    
    title = rashi_data.get("TITLE", "")
    if "(" in title:
        rashi_name = title.split("(")[0].strip()
    else:
        rashi_name = title.split("-")[0].strip()
    
    short_date = date.split("/")[0] + "/" + date.split("/")[1] if "/" in date else date
    
    content = rashi_data.get("content", {})
    highlight = extract_key_highlight(content)
    
    base = f"{rashi_name} દૈનિક રાશિફળ {short_date}"
    hashtags = " #shorts #viral"
    
    remaining_space = 100 - len(base) - len(hashtags) - 3
    
    if remaining_space > 15:
        if len(highlight) > remaining_space:
            highlight = highlight[:remaining_space-3] + "..."
        final_title = f"{base} | {highlight}{hashtags}"
    else:
        final_title = f"{base}{hashtags}"
    
    return final_title[:100]


def extract_key_highlight(content: Dict[str, str]) -> str:
    """Extract the most important/exciting phrase from content."""
    
    priority_keywords = [
        "ધન લાભ", "નફો", "સફળતા", "પ્રમોશન", "યોગ", 
        "પ્રેમ", "નાણાં", "ઉત્સાહ", "ખુશી", "શુભ", 
        "નવું", "આનંદ", "વિજય", "મજબૂત"
    ]
    
    for section_text in content.values():
        clean_text = " ".join(section_text.split())
        
        for keyword in priority_keywords:
            if keyword in clean_text:
                sentences = re.split('[.!?૥\n]', clean_text)
                for sentence in sentences:
                    if keyword in sentence:
                        highlight = sentence.strip()
                        highlight = highlight.replace("આજે ", "")
                        highlight = highlight.replace("તમારા માટે ", "")
                        highlight = highlight.replace("તમે ", "")
                        return highlight[:50]
    
    first_section = list(content.values())[0] if content else ""
    return " ".join(first_section.split())[:40]


# ==================== DESCRIPTION GENERATOR ====================
def generate_description(rashi_data: Dict, date: str) -> str:
    """Generate YouTube description from rashifal data."""
    
    title = rashi_data.get("TITLE", "")
    content = rashi_data.get("content", {})
    
    rashi_name = title.split("(")[0].strip() if "(" in title else title.split("-")[0].strip()
    
    description_parts = []
    
    description_parts.append(f"🌟 {rashi_name} - દૈનિક રાશિફળ 🌟")
    description_parts.append(f"📅 તારીખ: {date}\n")
    
    preview_count = 0
    for heading, text in content.items():
        if preview_count >= 3:
            break
        description_parts.append(f"✨ {heading}:")
        preview_text = text[:150] + "..." if len(text) > 150 else text
        description_parts.append(f"{preview_text}\n")
        preview_count += 1
    
    description_parts.append("\n📱 આ વિડિયો ગમે તો લાઈક અને શેર કરો!")
    description_parts.append("🔔 વધુ દૈનિક રાશિફળ માટે સબ્સ્ક્રાઈબ કરો!")
    description_parts.append("💬 કોમેન્ટમાં તમારી રાશિ જણાવો!\n")
    
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
def upload_video(file_path: str, title: str, description: str, tags: List[str] = None, playlist_id: str = None):
    """Upload a single video to YouTube."""
    
    print(f"\n📤 Uploading: {os.path.basename(file_path)}")
    print(f"   Title: {title}")
    
    try:
        service = get_youtube_service()
        
        media = MediaFileUpload(
            file_path,
            chunksize=-1,
            resumable=True,
            mimetype="video/*"
        )
        
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
        
        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:500],
                "categoryId": "24"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        request = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"      Upload progress: {progress}%", end="\r")
        
        print(f"\n   ✅ Upload complete!")
        print(f"   🎬 Video ID: {response['id']}")
        print(f"   🔗 URL: https://youtube.com/shorts/{response['id']}")
        
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
def upload_rashifal_batch(batch: str = "all", playlist_id: str = None):
    """
    Upload rashifal videos in batches.
    
    Args:
        batch: "batch1" (1-3), "batch2" (4-6), "batch3" (7-9), "batch4" (10-12), or "all"
        playlist_id: Optional YouTube playlist ID
    """
    
    # Define batch ranges
    batch_ranges = {
        "batch1": (0, 3, "1-3"),    # Rashis 1-3
        "batch2": (3, 6, "4-6"),    # Rashis 4-6
        "batch3": (6, 9, "7-9"),    # Rashis 7-9
        "batch4": (9, 12, "10-12")  # Rashis 10-12
    }
    
    print("\n" + "="*70)
    print("📤 YOUTUBE SHORTS BATCHED UPLOADER (4 BATCHES)")
    
    if batch in batch_ranges:
        start, end, label = batch_ranges[batch]
        print(f"   Uploading rashis {label} (Batch {batch[-1]}/4)")
    elif batch == "all":
        print("   Uploading ALL 12 rashis")
    else:
        print(f"   ❌ Invalid batch: {batch}")
        return
    
    print("="*70)
    
    if not os.path.exists(JSON_PATH):
        print(f"\n❌ ERROR: JSON file not found: {JSON_PATH}")
        return
    
    if not os.path.exists(OUTPUTS_DIR):
        print(f"\n❌ ERROR: Outputs directory not found: {OUTPUTS_DIR}")
        return
    
    try:
        rashifal_list, date = read_rashifal_json(JSON_PATH)
        print(f"\n✅ Date from JSON: {date}")
    except Exception as e:
        print(f"\n❌ JSON Error: {e}")
        return
    
    # Determine which rashis to upload
    if batch in batch_ranges:
        start, end, label = batch_ranges[batch]
        rashis_to_upload = rashifal_list[start:end]
        print(f"✅ Processing rashis {label} ({len(rashis_to_upload)} videos)\n")
    else:
        rashis_to_upload = rashifal_list  # All 12
        print(f"✅ Processing all 12 rashis\n")
    
    uploaded_count = 0
    failed_count = 0
    
    for rashi_data in rashis_to_upload:
        video_filename = rashi_data.get("OUTPUT_FILENAME")
        
        if not video_filename:
            print(f"⚠️ Skipping: No OUTPUT_FILENAME in JSON")
            continue
        
        video_path = os.path.join(OUTPUTS_DIR, video_filename)
        
        if not os.path.exists(video_path):
            print(f"⚠️ Video not found: {video_filename}")
            failed_count += 1
            continue
        
        smart_title = generate_smart_title(rashi_data, date)
        description = generate_description(rashi_data, date)
        
        print(f"\n{'='*70}")
        print(f"🎬 Processing: {video_filename}")
        print(f"   Generated Title: {smart_title}")
        print(f"   Length: {len(smart_title)} chars")
        
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
    
    print("\n" + "="*70)
    print(f"✅ BATCH UPLOAD COMPLETE!")
    print(f"   ✅ Uploaded: {uploaded_count}/{len(rashis_to_upload)}")
    print(f"   ❌ Failed: {failed_count}")
    print("="*70 + "\n")


# ==================== MAIN ====================
if __name__ == "__main__":
    playlist_id = os.getenv("YOUTUBE_PLAYLIST_ID", None)
    
    # Check if batch argument provided
    batch_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    valid_batches = ["batch1", "batch2", "batch3", "batch4", "all"]
    
    if batch_type not in valid_batches:
        print("Usage: python youtube_upload.py [batch1|batch2|batch3|batch4|all]")
        print("  batch1 - Upload rashis 1-3 (12 AM)")
        print("  batch2 - Upload rashis 4-6 (2 AM)")
        print("  batch3 - Upload rashis 7-9 (4 AM)")
        print("  batch4 - Upload rashis 10-12 (6 AM)")
        print("  all    - Upload all 12 rashis")
        sys.exit(1)
    
    upload_rashifal_batch(batch=batch_type, playlist_id=playlist_id)
