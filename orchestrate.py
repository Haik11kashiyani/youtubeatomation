"""
Orchestrator Script - Smart Batched Upload
- 6 AM: Generates 12 videos, uploads first 6, deletes them
- 7 AM: Uploads remaining 6, cleanup all
"""
import subprocess
import sys
import os
import shutil

def run_script(script_name: str, args: list = None) -> bool:
    """Run a Python script with optional arguments."""
    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*70}")
    print(f"🚀 Running: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {script_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {script_name} failed with error code: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False


def cleanup_uploaded_videos(batch: str):
    """
    Delete uploaded videos from outputs folder.
    
    Args:
        batch: "first" (delete first 6) or "second" (delete all remaining)
    """
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    
    if not os.path.exists(outputs_dir):
        print(f"⚠️ Outputs directory not found: {outputs_dir}")
        return
    
    # Get all MP4 files
    video_files = sorted([f for f in os.listdir(outputs_dir) if f.endswith('.mp4')])
    
    if not video_files:
        print("⚠️ No videos found to cleanup")
        return
    
    print(f"\n{'='*70}")
    print(f"🗑️  CLEANUP: Deleting uploaded videos")
    print(f"{'='*70}")
    
    if batch == "first":
        # Delete first 6 videos
        files_to_delete = video_files[:6]
        print(f"   Deleting first 6 uploaded videos...")
    else:
        # Delete all remaining videos
        files_to_delete = video_files
        print(f"   Deleting all remaining videos...")
    
    deleted_count = 0
    for filename in files_to_delete:
        file_path = os.path.join(outputs_dir, filename)
        try:
            os.remove(file_path)
            print(f"   ✅ Deleted: {filename}")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Error deleting {filename}: {e}")
    
    print(f"\n   📊 Total deleted: {deleted_count} videos")
    print(f"{'='*70}\n")


def cleanup_temp_files():
    """Delete temp_images folder."""
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_images")
    
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"   ✅ Deleted: temp_images/ folder")
        except Exception as e:
            print(f"   ⚠️ Error deleting temp_images/: {e}")


def main():
    """Main orchestration function."""
    
    # Check if this is batch 1 (6 AM) or batch 2 (7 AM)
    batch = sys.argv[1] if len(sys.argv) > 1 else "first"
    
    if batch not in ["first", "second"]:
        print("Usage: python orchestrate.py [first|second]")
        print("  first  - Generate videos and upload first 6 (6 AM run)")
        print("  second - Upload remaining 6 (7 AM run)")
        sys.exit(1)
    
    print("\n" + "="*70)
    if batch == "first":
        print("🌅 BATCH 1: Generate Videos + Upload First 6 Rashis (6 AM)")
    else:
        print("🌄 BATCH 2: Upload Remaining 6 Rashis (7 AM)")
    print("="*70)
    
    # Check if required files exist
    if not os.path.exists("build_shorts.py"):
        print("\n❌ ERROR: build_shorts.py not found!")
        sys.exit(1)
    
    if not os.path.exists("youtube_upload.py"):
        print("\n❌ ERROR: youtube_upload.py not found!")
        sys.exit(1)
    
    if batch == "first":
        # === BATCH 1: 6 AM RUN ===
        
        # Step 1: Generate all 12 videos
        print("\n📹 STEP 1: Generating All 12 Videos...")
        if not run_script("build_shorts.py"):
            print("\n❌ Video generation failed. Stopping.")
            sys.exit(1)
        
        # Step 2: Upload first 6 rashis
        print("\n📤 STEP 2: Uploading First 6 Rashis...")
        if not run_script("youtube_upload.py", ["first"]):
            print("\n❌ Upload failed for first batch.")
            sys.exit(1)
        
        # Step 3: Cleanup uploaded videos (first 6)
        print("\n🗑️  STEP 3: Cleaning Up First 6 Videos...")
        cleanup_uploaded_videos("first")
        
        # Step 4: Cleanup temp files
        print("\n🗑️  STEP 4: Cleaning Temp Files...")
        cleanup_temp_files()
        
        print("\n" + "="*70)
        print("✅ BATCH 1 COMPLETE!")
        print("   ✅ Generated: 12 videos")
        print("   ✅ Uploaded: First 6 rashis")
        print("   ✅ Cleaned: Uploaded videos + temp files")
        print("   ⏳ Waiting for 7 AM to upload remaining 6...")
        print("="*70 + "\n")
        
    else:
        # === BATCH 2: 7 AM RUN ===
        
        # Step 1: Upload remaining 6 rashis
        print("\n📤 STEP 1: Uploading Remaining 6 Rashis...")
        if not run_script("youtube_upload.py", ["second"]):
            print("\n❌ Upload failed for second batch.")
            sys.exit(1)
        
        # Step 2: Cleanup all remaining files
        print("\n🗑️  STEP 2: Final Cleanup...")
        cleanup_uploaded_videos("second")
        
        print("\n" + "="*70)
        print("✅ BATCH 2 COMPLETE!")
        print("   ✅ Uploaded: Remaining 6 rashis")
        print("   ✅ Total today: 12 videos")
        print("   ✅ All cleanup done!")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
