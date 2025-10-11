"""
Perfect Gujarati Rashifal Video Generator for YouTube Shorts
- Creates videos with image, title, and scrolling content
- ADDS BACKGROUND MUSIC from music folder
- Perfect Gujarati text using HTML rendering
- Auto-cleanup temp files
"""
import os
import json
from typing import List, Dict
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip, AudioFileClip
from PIL import Image

# Try to import playwright for HTML rendering
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not installed!")
    print("   Run: pip install playwright")
    print("   Then: playwright install chromium")

# ==================== CONFIGURATION ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "12 photos")
MUSIC_DIR = os.path.join(BASE_DIR, "music")  # Music folder with rashi subfolders
JSON_PATH = os.path.join(BASE_DIR, "rashifal_data.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEMP_DIR = os.path.join(BASE_DIR, "temp_images")

# Video settings for YouTube Shorts
WIDTH = 1080
HEIGHT = 1920
DURATION = 30.0
FPS = 30

# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: {width}px;
            height: {height}px;
            background: white;
            font-family: 'Noto Sans Gujarati', sans-serif;
            overflow: hidden;
        }}
        
        .title {{
            font-size: 52px;
            font-weight: 700;
            text-align: center;
            color: #000;
            padding: 15px 35px;
            line-height: 1.3;
            width: 80%;
            margin: 0 auto;
        }}
        
        .content {{
            font-size: 44px;
            font-weight: 400;
            text-align: left;
            color: #000;
            padding: 0 45px;
            line-height: 1.7;
            width: 80%;
            margin: 0 auto;
        }}
        
        .section {{
            margin-bottom: 25px;
        }}
        
        .section-heading {{
            font-weight: 700;
            color: #000;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

# ==================== SETUP ====================
def ensure_directories():
    """Create necessary directories."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(MUSIC_DIR, exist_ok=True)
    print(f"✅ Output directory: {OUTPUT_DIR}")
    print(f"✅ Temp directory: {TEMP_DIR}")
    print(f"✅ Music directory: {MUSIC_DIR}")


def read_rashifal_json(json_path: str) -> List[Dict]:
    """Read rashifal data from JSON."""
    print(f"\n📖 Reading JSON: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rashifal_list = data["rashifal"]
    date = data.get("date", "")
    
    print(f"✅ Date: {date}")
    print(f"✅ Total Rashis: {len(rashifal_list)}")
    
    return rashifal_list


# ==================== HTML RENDERING ====================
def render_html_to_image(html_content: str, output_path: str, width: int, height: int):
    """Render HTML to PNG image using Playwright."""
    
    if not PLAYWRIGHT_AVAILABLE:
        print(f"      ❌ Cannot render - Playwright not installed!")
        return False
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': width, 'height': height})
            
            # Load HTML
            page.set_content(html_content)
            
            # Wait for fonts to load
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(500)
            
            # Screenshot
            page.screenshot(path=output_path, full_page=False)
            
            browser.close()
        
        return True
        
    except Exception as e:
        print(f"      ❌ HTML rendering error: {e}")
        return False


# ==================== CONTENT FORMATTING ====================
def format_content_sections(content_dict: Dict[str, str]) -> str:
    """Format content dictionary as HTML with proper sections."""
    html_sections = []
    
    for heading, text in content_dict.items():
        section_html = f'''
        <div class="section">
            <div class="section-heading">{heading}:</div>
            <div>{text}</div>
        </div>
        '''
        html_sections.append(section_html)
    
    return "\n".join(html_sections)


def split_content_into_pages(content_dict: Dict[str, str], sections_per_page: int = 2) -> List[str]:
    """Split content into multiple pages for scrolling effect."""
    items = list(content_dict.items())
    pages = []
    
    for i in range(0, len(items), sections_per_page):
        page_items = dict(items[i:i + sections_per_page])
        page_html = format_content_sections(page_items)
        pages.append(page_html)
    
    return pages


# ==================== IMAGE HANDLING ====================
def find_image(filename: str) -> str:
    """Find rashi image in assets directory."""
    if not filename:
        return None
    
    print(f"      🔍 Looking for image: {filename}")
    
    # Try exact filename first
    candidate = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(candidate):
        print(f"         ✅ Found!")
        return candidate
    
    # Try different extensions
    name = os.path.splitext(filename)[0]
    for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
        candidate = os.path.join(ASSETS_DIR, name + ext)
        if os.path.exists(candidate):
            print(f"         ✅ Found!")
            return candidate
    
    print(f"         ❌ Not found!")
    return None


# ==================== MUSIC HANDLING ====================
def find_music_for_rashi(rashi_name: str, image_filename: str) -> str:
    """
    Find random background music for a rashi from its folder.
    Looks in music/<rashi_folder>/ and picks a random MP3/WAV file.
    """
    import random
    
    if not rashi_name and not image_filename:
        return None
    
    # Extract rashi folder name from image filename (e.g., "mesh.jpg" -> "Mesh")
    rashi_folder = os.path.splitext(image_filename)[0].capitalize() if image_filename else rashi_name
    
    print(f"      🎵 Looking for music in folder: {rashi_folder}")
    
    # Path to rashi music folder
    rashi_music_dir = os.path.join(MUSIC_DIR, rashi_folder)
    
    if not os.path.exists(rashi_music_dir):
        print(f"         ❌ Music folder not found: {rashi_music_dir}")
        return None
    
    # Find all music files in the folder
    music_files = [
        f for f in os.listdir(rashi_music_dir) 
        if f.endswith(('.mp3', '.wav', '.m4a', '.MP3', '.WAV', '.M4A'))
    ]
    
    if not music_files:
        print(f"         ❌ No music files found in: {rashi_music_dir}")
        return None
    
    # Pick a random music file
    selected_music = random.choice(music_files)
    music_path = os.path.join(rashi_music_dir, selected_music)
    
    print(f"         ✅ Found {len(music_files)} music files")
    print(f"         🎲 Randomly selected: {selected_music}")
    
    return music_path


# ==================== VIDEO COMPOSITION ====================
def compose_video(data: Dict, video_index: int) -> CompositeVideoClip:
    """
    Compose video with:
    1. Rashi image (top, 35% height, fixed)
    2. Title (below image, fixed, bold)
    3. Content (scrolling pages)
    4. Background music (if available)
    """
    
    title = data["TITLE"]
    content_dict = data["content"]
    image_file = data["IMAGE"]
    output_filename = data["OUTPUT_FILENAME"]
    
    # Extract rashi name for music folder matching
    rashi_name = title.split("(")[0].strip() if "(" in title else ""
    
    print(f"\n🎬 Creating: {output_filename}")
    print(f"   Title: {title[:50]}...")
    
    layers = []
    y_position = 0
    
    # === WHITE BACKGROUND ===
    bg = ColorClip(size=(WIDTH, HEIGHT), color=(255, 255, 255)).set_duration(DURATION)
    layers.append(bg)
    
    # === RASHI IMAGE (35% HEIGHT, FIXED AT TOP) ===
    y_position = 40  # Start from top with small margin
    
    img_path = find_image(image_file)
    if img_path:
        try:
            print(f"      ✅ Loading image: {img_path}")
            
            # Open image with PIL to check dimensions
            pil_img = Image.open(img_path)
            print(f"         Original size: {pil_img.size}")
            
            # Create MoviePy ImageClip
            img_clip = ImageClip(img_path)
            
            # Make image 35% of video height (bigger and more visible)
            target_height = int(HEIGHT * 0.35)  # 35% of 1920 = 672px
            
            # Calculate target width maintaining aspect ratio
            aspect_ratio = pil_img.width / pil_img.height
            target_width = int(target_height * aspect_ratio)
            
            # Don't exceed 70% of screen width
            max_width = int(WIDTH * 0.70)
            if target_width > max_width:
                target_width = max_width
                target_height = int(target_width / aspect_ratio)
            
            # Resize using PIL directly to avoid MoviePy's ANTIALIAS issue
            pil_img_resized = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Save temporarily and reload as ImageClip
            temp_resized_path = os.path.join(TEMP_DIR, f"resized_image_{video_index}.png")
            pil_img_resized.save(temp_resized_path)
            img_clip = ImageClip(temp_resized_path)
            
            print(f"         Resized to width: {target_width}px, height: {target_height}px (35% of video height)")
            
            # Position at center horizontally, near top vertically
            img_clip = img_clip.set_position(("center", y_position))
            img_clip = img_clip.set_duration(DURATION)
            
            layers.append(img_clip)
            
            y_position += target_height + 30  # Add spacing after image
            
            print(f"      ✅ Image added successfully at y={y_position - target_height - 30}")
            
        except Exception as e:
            print(f"      ❌ Image error: {e}")
            import traceback
            traceback.print_exc()
            y_position += 300  # Fallback spacing
    else:
        print(f"      ⚠️ Image not found, skipping: {image_file}")
        y_position += 300  # Fallback spacing
    
    # === TITLE (FIXED BELOW IMAGE) ===
    print(f"      📝 Rendering title...")
    
    title_html = HTML_TEMPLATE.format(
        width=WIDTH,
        height=180,
        content=f'<div class="title">{title}</div>'
    )
    
    title_img_path = os.path.join(TEMP_DIR, f"title_{video_index}.png")
    
    if render_html_to_image(title_html, title_img_path, WIDTH, 180):
        title_clip = ImageClip(title_img_path)
        title_clip = title_clip.set_position((0, y_position)).set_duration(DURATION)
        layers.append(title_clip)
        y_position += 180 + 25
        print(f"      ✅ Title added at y={y_position - 205}")
    else:
        print(f"      ❌ Title rendering failed!")
        y_position += 180
    
    # === CONTENT (SCROLLING/PAGING) ===
    available_height = HEIGHT - y_position - 60  # More bottom padding to prevent cutting
    
    # Ensure minimum height for content
    if available_height < 800:
        print(f"      ⚠️ Warning: Limited space for content ({available_height}px)")
    
    # Split content into pages (2 sections per page to avoid cutting)
    pages = split_content_into_pages(content_dict, sections_per_page=2)
    
    print(f"      📄 Content pages: {len(pages)}")
    print(f"      📏 Available height for content: {available_height}px")
    
    # Calculate time per page
    time_per_page = DURATION / len(pages)
    current_time = 0.0
    
    for page_idx, page_html in enumerate(pages):
        print(f"      📝 Rendering page {page_idx + 1}/{len(pages)}...")
        
        # Create full HTML for this page
        content_html = HTML_TEMPLATE.format(
            width=WIDTH,
            height=available_height,
            content=f'<div class="content">{page_html}</div>'
        )
        
        page_img_path = os.path.join(TEMP_DIR, f"content_{video_index}_page_{page_idx}.png")
        
        if render_html_to_image(content_html, page_img_path, WIDTH, available_height):
            # Create clip for this page
            page_clip = ImageClip(page_img_path)
            page_clip = page_clip.set_start(current_time)
            page_clip = page_clip.set_duration(min(time_per_page, DURATION - current_time))
            page_clip = page_clip.set_position((0, y_position))
            
            # Add smooth transitions
            page_clip = page_clip.crossfadein(0.5).crossfadeout(0.5)
            
            layers.append(page_clip)
            print(f"         ✅ Page {page_idx + 1} added")
        else:
            print(f"         ❌ Page {page_idx + 1} rendering failed!")
        
        current_time += time_per_page
    
    # === COMPOSE VIDEO ===
    print(f"      🎞️ Composing {len(layers)} layers...")
    video = CompositeVideoClip(layers, size=(WIDTH, HEIGHT)).set_duration(DURATION)
    
    # === ADD BACKGROUND MUSIC ===
    music_path = find_music_for_rashi(rashi_name, image_file)
    if music_path:
        try:
            print(f"      🎵 Adding background music: {os.path.basename(music_path)}")
            audio = AudioFileClip(music_path)
            
            # Loop or trim audio to match video duration
            if audio.duration < DURATION:
                # Loop the audio
                loops_needed = int(DURATION / audio.duration) + 1
                audio = audio.loop(n=loops_needed)
            
            # Trim to exact duration
            audio = audio.subclip(0, DURATION)
            
            # Set volume (1.0 = 100% volume - full volume)
            audio = audio.volumex(1.0)
            
            # Add audio to video
            video = video.set_audio(audio)
            
            print(f"      ✅ Background music added successfully!")
            
        except Exception as e:
            print(f"      ❌ Music error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"      ⚠️ No music added (not found for this rashi)")
    
    return video


# ==================== MAIN ====================
def main():
    """Main execution - Generate all 12 rashifal videos with music."""
    
    print("\n" + "="*70)
    print("🎥 GUJARATI RASHIFAL VIDEO GENERATOR FOR YOUTUBE SHORTS")
    print("   ✅ Perfect Gujarati Text (HTML Rendering)")
    print("   ✅ Background Music from music/<rashi>/ folders (random selection)")
    print("   ✅ Image (35% height) + Title + Content (Scrolling)")
    print("="*70)
    
    # Check Playwright
    if not PLAYWRIGHT_AVAILABLE:
        print("\n❌ ERROR: Playwright is required!")
        print("\n📦 Install with:")
        print("   pip install playwright")
        print("   playwright install chromium")
        print("\n")
        return
    
    # Setup directories
    ensure_directories()
    
    # Check assets directory
    if not os.path.exists(ASSETS_DIR):
        print(f"\n⚠️ WARNING: Assets directory not found: {ASSETS_DIR}")
        print(f"   Creating it now...")
        os.makedirs(ASSETS_DIR, exist_ok=True)
        print(f"   Please place your 12 rashi images in: {ASSETS_DIR}")
    else:
        print(f"\n✅ Assets directory found: {ASSETS_DIR}")
        image_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'))]
        print(f"   Found {len(image_files)} images")
    
    # Check music directory
    if os.path.exists(MUSIC_DIR):
        # Count rashi folders
        rashi_folders = [d for d in os.listdir(MUSIC_DIR) if os.path.isdir(os.path.join(MUSIC_DIR, d))]
        print(f"\n✅ Music directory found: {MUSIC_DIR}")
        print(f"   Found {len(rashi_folders)} rashi music folders:")
        
        total_music_files = 0
        for folder in rashi_folders:
            folder_path = os.path.join(MUSIC_DIR, folder)
            music_count = len([f for f in os.listdir(folder_path) if f.endswith(('.mp3', '.wav', '.m4a'))])
            print(f"      - {folder}/ ({music_count} music files)")
            total_music_files += music_count
        
        print(f"   📊 Total: {total_music_files} music files across all rashis")
    else:
        print(f"\n⚠️ Music directory not found: {MUSIC_DIR}")
        print(f"   Videos will be created WITHOUT background music")
        print(f"   To add music: Create 'music' folder with rashi subfolders")
    
    # Check JSON file
    if not os.path.exists(JSON_PATH):
        print(f"\n❌ ERROR: JSON file not found: {JSON_PATH}")
        print("   Please save your JSON as 'rashifal_data.json'")
        return
    
    # Read data
    try:
        rashifal_data = read_rashifal_json(JSON_PATH)
    except Exception as e:
        print(f"\n❌ JSON Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Generate videos
    success_count = 0
    total = len(rashifal_data)
    
    for idx, rashi in enumerate(rashifal_data):
        try:
            print(f"\n{'='*70}")
            print(f"📹 Processing {idx + 1}/{total}: {rashi['TITLE'][:40]}...")
            print(f"{'='*70}")
            
            output_path = os.path.join(OUTPUT_DIR, rashi["OUTPUT_FILENAME"])
            
            # Create video
            video_clip = compose_video(rashi, idx)
            
            # Render to MP4
            print(f"\n      🎬 Rendering MP4: {rashi['OUTPUT_FILENAME']}")
            print(f"      ⏳ Please wait (this takes 1-2 minutes per video)...")
            
            video_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=FPS,
                preset="medium",
                bitrate="8000k",
                threads=4,
                logger=None  # Suppress verbose output
            )
            
            print(f"\n✅ SUCCESS: {rashi['OUTPUT_FILENAME']}")
            print(f"   📹 Video saved: {output_path}")
            print(f"   📺 YouTube Title: {rashi.get('YOUTUBE_SHORT_TITLE', '')[:60]}...")
            print(f"   🎵 Music added: Random from {os.path.splitext(rashi['IMAGE'])[0].capitalize()} folder")
            
            success_count += 1
            
        except Exception as e:
            print(f"\n❌ ERROR in video {idx + 1}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Summary
    print("\n" + "="*70)
    print(f"✅ COMPLETE! {success_count}/{total} videos created successfully")
    print(f"\n📁 Videos location: {OUTPUT_DIR}")
    
    # Clean up temp images folder
    if os.path.exists(TEMP_DIR):
        try:
            import shutil
            shutil.rmtree(TEMP_DIR)
            print(f"🗑️  Temp images folder deleted: {TEMP_DIR}")
        except Exception as e:
            print(f"⚠️  Could not delete temp folder: {e}")
    
    print("\n📤 NEXT STEPS:")
    print("   1. Videos are ready with background music!")
    print("   2. Run youtube_upload.py to upload all videos")
    print("   3. Videos will auto-upload with titles and descriptions")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()