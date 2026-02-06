"""
Rename Lesson 10 days files from days_ to time_ prefix
"""

import os
import shutil

# Mapping of old names to new names
RENAME_MAP = {
    "lesson_10_days_monday.png": "lesson_10_time_monday.png",
    "lesson_10_days_tuesday.png": "lesson_10_time_tuesday.png",
    "lesson_10_days_wednesday.png": "lesson_10_time_wednesday.png",
    "lesson_10_days_thursday.png": "lesson_10_time_thursday.png",
    "lesson_10_days_friday.png": "lesson_10_time_friday.png",
    "lesson_10_days_saturday.png": "lesson_10_time_saturday.png",
    "lesson_10_days_sunday.png": "lesson_10_time_sunday.png",
}

def rename_files(directory):
    """Rename files in the directory."""
    
    print("=" * 70)
    print("RENAMING LESSON 10 DAYS FILES")
    print("=" * 70)
    
    renamed = 0
    
    for old_name, new_name in RENAME_MAP.items():
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"✅ {old_name} → {new_name}")
            renamed += 1
        else:
            print(f"⚠️  NOT FOUND: {old_name}")
    
    print("\n" + "=" * 70)
    print(f"✅ Renamed {renamed} files")
    print("=" * 70)


if __name__ == "__main__":
    directory = r"C:\GitHub\ArmenianTutor\ArmenianAITutor\image_library"
    
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        input("Press Enter to exit...")
        exit(1)
    
    print(f"Directory: {directory}\n")
    
    response = input("Rename 7 files? (yes/no): ").strip().lower()
    
    if response == 'yes':
        rename_files(directory)
        print("\n✅ Done! Files renamed successfully.")
        print("\nYou can now commit and push to GitHub.")
    else:
        print("Cancelled")
    
    input("\nPress Enter to exit...")
