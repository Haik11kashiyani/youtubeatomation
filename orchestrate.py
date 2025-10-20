"""
Orchestrator Script - 4 Batches Upload System
- 11 PM: Generates 12 videos
- 12 AM: Uploads rashis 1-3, deletes ONLY those 3
- 2 AM: Uploads rashis 4-6, deletes ONLY those 3
- 4 AM: Uploads rashis 7-9, deletes ONLY those 3
- 6 AM: Uploads rashis 10-12, deletes those 3
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


def get_batch_files_from_json(batch_number: int):
    """
    Get list of files for specific batch from rashifal_data.json.
    
    Args:
        batch_number: 1 (rashis 1-3), 2 (rashis 4-6), 3 (rashis 7-9), 4 (rashis 10-12)
    
    Returns:
        List of OUTPUT_FILENAME for the batch
    """
    json_path = os.path.join(os.path.dirname(__file__), "rashifal_data.json")
    
    if not os.path.exists(json_path):
        print(f"⚠️ rashifal_data.json not found")
        return []
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle new structure with rashifal_dates
        if "rashifal_dates" in data:
            rashifal_list = data["rashifal_dates"][0]["rashifal"]
        else:
            rashifal_list = data.get("rashifal", [])
        
        # Define batch ranges
        batch_ranges = {
            1: (0, 3),    # Rashis 1-3
            2: (3, 6),    # Rashis 4-6
            3: (6, 9),    # Rashis 7-9
            4: (9, 12)    # Rashis 10-12
        }
        
        if batch_number not in batch_ranges:
            print(f"⚠️ Invalid batch number: {batch_number}")
            return []
        
        start, end = batch_ranges[batch_number]
        
        # Get filenames for this batch
        batch_files = [
            rashi.get("OUTPUT_FILENAME") 
            for rashi in rashifal_list[start:end]
            if rashi.get("OUTPUT_FILENAME")
        ]
        
        return batch_files
        
    except Exception as e:
        print(f"⚠️ Error reading JSON: {e}")
        return []


def cleanup_uploaded_videos(batch_files: list = None):
    """
    Delete uploaded videos from outputs folder.
    
    Args:
        batch_files: List of filenames to delete
    """
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    
    if not os.path.exists(outputs_dir):
        print(f"⚠️ Outputs directory not found: {outputs_dir}")
        return
    
    print(f"\n{'='*70}")
    print(f"🗑️  CLEANUP: Deleting uploaded videos")
    print(f"{'='*70}")
    
    if not batch_files:
        print(f"   ⚠️ No files to delete")
        return
    
    print(f"   Deleting {len(batch_files)} uploaded videos...")
    print(f"   Files: {', '.join([f.split('-')[0] for f in batch_files])}")
    
    deleted_count = 0
    for filename in batch_files:
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


def count_remaining_videos():
    """Count how many videos remain in outputs folder."""
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    if os.path.exists(outputs_dir):
        return len([f for f in os.listdir(outputs_dir) if f.endswith('.mp4')])
    return 0


def main():
    """Main orchestration function."""
    
    # Check which stage to run
    stage = sys.argv[1] if len(sys.argv) > 1 else "generate"
    
    valid_stages = ["generate", "batch1", "batch2", "batch3", "batch4"]
    
    if stage not in valid_stages:
        print("Usage: python orchestrate.py [generate|batch1|batch2|batch3|batch4]")
        print("  generate - Generate all 12 videos (11 PM)")
        print("  batch1   - Upload rashis 1-3 (12 AM)")
        print("  batch2   - Upload rashis 4-6 (2 AM)")
        print("  batch3   - Upload rashis 7-9 (4 AM)")
        print("  batch4   - Upload rashis 10-12 (6 AM)")
        sys.exit(1)
    
    # Check if required files exist
    if not os.path.exists("build_shorts.py"):
        print("\n❌ ERROR: build_shorts.py not found!")
        sys.exit(1)
    
    if not os.path.exists("youtube_upload.py"):
        print("\n❌ ERROR: youtube_upload.py not found!")
        sys.exit(1)
    
    print("\n" + "="*70)
    
    if stage == "generate":
        # === GENERATION STAGE: 11 PM ===
        print("🌙 GENERATION: Create All 12 Videos (11:00 PM IST)")
        print("="*70)
        
        # Generate all 12 videos
        print("\n📹 STEP 1: Generating All 12 Videos...")
        success, output = run_script("build_shorts.py")
        if not success:
            print("\n❌ Video generation failed. Stopping.")
            sys.exit(1)
        
        # Cleanup temp files
        print("\n🗑️  STEP 2: Cleaning Temp Files...")
        cleanup_temp_files()
        
        # Summary
        video_count = count_remaining_videos()
        print("\n" + "="*70)
        print("✅ GENERATION COMPLETE!")
        print(f"   ✅ Generated: {video_count} videos with music")
        print("   ✅ All videos saved in outputs/ folder")
        print("   ✅ Temp files cleaned")
        print("   ⏳ Waiting for 12:00 AM to start uploads...")
        print("="*70 + "\n")
        
    elif stage in ["batch1", "batch2", "batch3", "batch4"]:
        # === UPLOAD BATCHES ===
        batch_number = int(stage[-1])  # Extract number from "batch1", "batch2", etc.
        
        batch_labels = {
            1: ("1-3", "12:00 AM", "🌅"),
            2: ("4-6", "2:00 AM", "🌄"),
            3: ("7-9", "4:00 AM", "🌆"),
            4: ("10-12", "6:00 AM", "☀️")
        }
        
        rashi_range, time_label, emoji = batch_labels[batch_number]
        
        print(f"{emoji} BATCH {batch_number}: Upload Rashis {rashi_range} ({time_label})")
        print("="*70)
        
        # Check available videos
        video_count_before = count_remaining_videos()
        print(f"\n📊 Videos available before upload: {video_count_before}")
        
        if video_count_before == 0:
            print("\n⚠️ WARNING: No videos found in outputs folder!")
            print("   Either generation didn't run or files were deleted.")
            sys.exit(1)
        
        # Get list of files for this batch
        batch_files = get_batch_files_from_json(batch_number)
        if batch_files:
            print(f"📋 Will upload: {', '.join([f.split('-')[0] for f in batch_files])}")
        
        # Upload this batch
        print(f"\n📤 STEP 1: Uploading Rashis {rashi_range}...")
        success, output = run_script("youtube_upload.py", [stage])
        if not success:
            print(f"\n❌ Upload failed for batch {batch_number}.")
            sys.exit(1)
        
        # Cleanup ONLY uploaded videos
        print(f"\n🗑️  STEP 2: Cleaning Up Uploaded Videos...")
        cleanup_uploaded_videos(batch_files)
        
        # Summary
        video_count_after = count_remaining_videos()
        print("\n" + "="*70)
        print(f"✅ BATCH {batch_number} COMPLETE!")
        print(f"   ✅ Uploaded: Rashis {rashi_range} (3 videos)")
        print(f"   ✅ Cleaned: 3 uploaded videos")
        print(f"   📊 Remaining videos: {video_count_after}")
        
        if batch_number < 4:
            next_batch = batch_number + 1
            next_time = batch_labels[next_batch][1]
            print(f"   ⏳ Waiting for {next_time} to upload next batch...")
        else:
            print("   🎉 All 12 videos uploaded successfully!")
            print("   ✅ Daily automation complete!")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
