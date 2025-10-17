"""
Orchestrator Script - Smart Batched Upload (FIXED CLEANUP)
- 6 AM: Generates 12 videos, uploads first 6, deletes ONLY uploaded ones
- 7 AM: Uploads remaining 6, cleanup all
"""
import subprocess
import sys
import os
import shutil
import json

def run_script(script_name: str, args: list = None) -> tuple:
    """
    Run a Python script with optional arguments.
    Returns: (success: bool, output: str)
    """
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
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"\n✅ {script_name} completed successfully!")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {script_name} failed with error code: {e.returncode}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False, e.stdout if e.stdout else ""
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False, ""


def get_uploaded_files_from_json():
    """
    Get list of files that should be in first batch (rashis 1-6).
    Returns list of filenames based on rashifal_data.json order.
    """
    json_path = os.path.join(os.path.dirname(__file__), "rashifal_data.json")
    
    if not os.path.exists(json_path):
        print(f"⚠️ rashifal_data.json not found")
        return []
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        rashifal_list = data.get("rashifal", [])
        
        # Get first 6 rashis' OUTPUT_FILENAME
        first_6_files = [
            rashi.get("OUTPUT_FILENAME") 
            for rashi in rashifal_list[:6]
            if rashi.get("OUTPUT_FILENAME")
        ]
        
        return first_6_files
        
    except Exception as e:
        print(f"⚠️ Error reading JSON: {e}")
        return []


def cleanup_uploaded_videos(batch: str, uploaded_files: list = None):
    """
    Delete uploaded videos from outputs folder.
    
    Args:
        batch: "first" (delete specific uploaded files) or "second" (delete all)
        uploaded_files: List of filenames that were uploaded in batch 1
    """
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    
    if not os.path.exists(outputs_dir):
        print(f"⚠️ Outputs directory not found: {outputs_dir}")
        return
    
    print(f"\n{'='*70}")
    print(f"🗑️  CLEANUP: Deleting uploaded videos")
    print(f"{'='*70}")
    
    if batch == "first":
        if uploaded_files:
            # Delete only the files that were uploaded
            files_to_delete = uploaded_files
            print(f"   Deleting {len(files_to_delete)} uploaded videos (first 6 rashis)...")
            print(f"   Files to delete: {', '.join([f.split('-')[0] for f in files_to_delete])}")
        else:
            print(f"   ⚠️ No upload list provided, skipping cleanup")
            return
    else:
        # Batch 2: Delete all remaining
        files_to_delete = [f for f in os.listdir(outputs_dir) if f.endswith('.mp4')]
        print(f"   Deleting all remaining videos...")
    
    deleted_count = 0
    for filename in files_to_delete:
        file_path = os.path.join(outputs_dir, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   ✅ Deleted: {filename}")
                deleted_count += 1
            else:
                print(f"   ⚠️ File not found (already deleted?): {filename}")
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
        success, output = run_script("build_shorts.py")
        if not success:
            print("\n❌ Video generation failed. Stopping.")
            sys.exit(1)
        
        # Step 2: Get list of first 6 rashis from JSON (the ones we'll upload)
        print("\n📋 Getting list of first 6 rashis to upload...")
        first_6_files = get_uploaded_files_from_json()
        if first_6_files:
            print(f"   First 6 files: {', '.join([f.split('-')[0] for f in first_6_files])}")
        
        # Step 3: Upload first 6 rashis
        print("\n📤 STEP 2: Uploading First 6 Rashis...")
        success, output = run_script("youtube_upload.py", ["first"])
        if not success:
            print("\n❌ Upload failed for first batch.")
            sys.exit(1)
        
        # Step 4: Cleanup ONLY the uploaded videos (first 6 from JSON order)
        print("\n🗑️  STEP 3: Cleaning Up ONLY Uploaded Videos...")
        cleanup_uploaded_videos("first", first_6_files)
        
        # Step 5: Cleanup temp files
        print("\n🗑️  STEP 4: Cleaning Temp Files...")
        cleanup_temp_files()
        
        # Step 6: Verify remaining videos
        outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
        remaining = [f for f in os.listdir(outputs_dir) if f.endswith('.mp4')] if os.path.exists(outputs_dir) else []
        
        print("\n" + "="*70)
        print("✅ BATCH 1 COMPLETE!")
        print("   ✅ Generated: 12 videos")
        print("   ✅ Uploaded: First 6 rashis")
        print("   ✅ Cleaned: Uploaded videos + temp files")
        print(f"   📊 Remaining for Batch 2: {len(remaining)} videos")
        if remaining:
            print(f"   📹 Waiting videos: {', '.join([f.split('-')[0] for f in remaining])}")
        print("   ⏳ Waiting for 7 AM to upload remaining 6...")
        print("="*70 + "\n")
        
    else:
        # === BATCH 2: 7 AM RUN ===
        
        # Step 1: Verify we have videos to upload
        outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
        remaining = [f for f in os.listdir(outputs_dir) if f.endswith('.mp4')] if os.path.exists(outputs_dir) else []
        
        if not remaining:
            print("\n⚠️ WARNING: No videos found in outputs folder!")
            print("   This means either:")
            print("   1. Batch 1 didn't run yet")
            print("   2. Videos were already uploaded")
            print("   3. Cleanup happened incorrectly")
        else:
            print(f"\n✅ Found {len(remaining)} videos ready to upload")
            print(f"   Videos: {', '.join([f.split('-')[0] for f in remaining])}")
        
        # Step 2: Upload remaining 6 rashis
        print("\n📤 STEP 1: Uploading Remaining 6 Rashis...")
        success, output = run_script("youtube_upload.py", ["second"])
        if not success:
            print("\n❌ Upload failed for second batch.")
            sys.exit(1)
        
        # Step 3: Cleanup all remaining files
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
