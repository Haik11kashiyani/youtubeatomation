"""
Orchestrator Script
Runs build_shorts.py first, then youtube_upload.py
For GitHub Actions sequential execution
"""
import subprocess
import sys
import os

def run_script(script_name: str) -> bool:
    """Run a Python script and return success status."""
    print(f"\n{'='*70}")
    print(f"🚀 Running: {script_name}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
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


def main():
    """Main orchestration function."""
    print("\n" + "="*70)
    print("🎬 GUJARATI RASHIFAL AUTOMATION")
    print("   Step 1: Generate videos (build_shorts.py)")
    print("   Step 2: Upload to YouTube (youtube_upload.py)")
    print("="*70)
    
    # Check if required files exist
    if not os.path.exists("build_shorts.py"):
        print("\n❌ ERROR: build_shorts.py not found!")
        sys.exit(1)
    
    if not os.path.exists("youtube_upload.py"):
        print("\n❌ ERROR: youtube_upload.py not found!")
        sys.exit(1)
    
    # Step 1: Generate videos
    print("\n📹 STEP 1: Generating Videos...")
    if not run_script("build_shorts.py"):
        print("\n❌ Video generation failed. Stopping.")
        sys.exit(1)
    
    # Step 2: Upload videos
    print("\n📤 STEP 2: Uploading to YouTube...")
    if not run_script("youtube_upload.py"):
        print("\n❌ Upload failed. Check logs above.")
        sys.exit(1)
    
    # Success
    print("\n" + "="*70)
    print("✅ ALL DONE! Videos generated and uploaded successfully!")
    print("="*70 + "\n")
    
    # Step 3: Cleanup - Delete generated videos and temp files
    print("\n🗑️  STEP 3: Cleaning up...")
    cleanup_files()


def cleanup_files():
    """Delete generated videos and temporary files after upload."""
    import shutil
    
    print("\n" + "="*70)
    print("🗑️  CLEANUP: Deleting temporary files")
    print("="*70)
    
    deleted_count = 0
    
    # Delete outputs folder (generated videos)
    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    if os.path.exists(outputs_dir):
        try:
            for file in os.listdir(outputs_dir):
                file_path = os.path.join(outputs_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"   ✅ Deleted: {file}")
                    deleted_count += 1
            print(f"\n   📂 Cleaned outputs/ folder ({deleted_count} files deleted)")
        except Exception as e:
            print(f"   ⚠️ Error cleaning outputs/: {e}")
    
    # Delete temp_images folder
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_images")
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"   ✅ Deleted: temp_images/ folder")
        except Exception as e:
            print(f"   ⚠️ Error deleting temp_images/: {e}")
    
    print("\n✅ Cleanup complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()