"""
HAM10000 Dataset Setup
Downloads from Kaggle and organizes files for training.

Prerequisites:
  pip install kaggle
  Place kaggle.json in ~/.kaggle/  (from https://www.kaggle.com/settings/account)
"""

import os
import shutil
import zipfile
from pathlib import Path


DATA_DIR   = Path("data/ham10000")
IMAGES_DIR = DATA_DIR / "images"
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def check_kaggle_credentials():
    creds = Path.home() / ".kaggle" / "kaggle.json"
    if not creds.exists():
        print("ERROR: kaggle.json not found at ~/.kaggle/kaggle.json")
        print("\nSteps to fix:")
        print("  1. Go to https://www.kaggle.com/settings/account")
        print("  2. Click 'Create New API Token'")
        print("  3. Move the downloaded kaggle.json to ~/.kaggle/")
        print("  4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    return True


def download_dataset():
    print("Downloading HAM10000 from Kaggle...")
    try:
        # Check if data already downloaded
        existing_images = len(list(IMAGES_DIR.glob("*.jpg")))
        if existing_images > 100:
            print(f"  ✓ Images already present ({existing_images} found), skipping download.")
            return
        
        result = os.system(
            "kaggle datasets download -d kmader/skin-lesion-analysis-toward-melanoma-detection "
            f"-p {DATA_DIR} --unzip"
        )
        
        if result != 0:
            raise RuntimeError("Kaggle download failed. Check your kaggle.json credentials.")
        print("  ✓ Download complete")
    except Exception as e:
        print(f"  ✗ Download error: {e}")
        raise


def organize_images():
    """Merge HAM10000_images_part1 and HAM10000_images_part2 into a single images/ dir."""
    print("\nOrganizing images...")
    moved = 0

    for part in ["HAM10000_images_part1", "HAM10000_images_part2"]:
        part_dir = DATA_DIR / part
        if part_dir.exists():
            for img in part_dir.glob("*.jpg"):
                shutil.move(str(img), str(IMAGES_DIR / img.name))
                moved += 1
            part_dir.rmdir()

    print(f"  Moved {moved} images → {IMAGES_DIR}")

    # Verify metadata CSV
    csv_candidates = list(DATA_DIR.glob("HAM10000_metadata*.csv"))
    if csv_candidates:
        target = DATA_DIR / "HAM10000_metadata.csv"
        if csv_candidates[0] != target:
            shutil.copy(str(csv_candidates[0]), str(target))
        print(f"  Metadata CSV: {target}")
    else:
        print("  WARNING: HAM10000_metadata.csv not found!")


def verify():
    import pandas as pd
    csv_path = DATA_DIR / "HAM10000_metadata.csv"
    if not csv_path.exists():
        print("ERROR: Metadata CSV missing.")
        return

    df = pd.read_csv(csv_path)
    images_found = len(list(IMAGES_DIR.glob("*.jpg")))
    print(f"\n── Dataset Summary ──────────────────")
    print(f"  CSV rows:      {len(df)}")
    print(f"  Images found:  {images_found}")
    print(f"  Class counts:")
    for cls, cnt in df["dx"].value_counts().items():
        print(f"    {cls:8s}: {cnt}")

    missing = 0
    for _, row in df.iterrows():
        if not (IMAGES_DIR / f"{row['image_id']}.jpg").exists():
            missing += 1
    if missing:
        print(f"\n  WARNING: {missing} images referenced in CSV but not found.")
    else:
        print(f"\n  ✓ All images present.")


if __name__ == "__main__":
    if not check_kaggle_credentials():
        exit(1)
    download_dataset()
    organize_images()
    verify()
    print("\nDone! Run train.py to start training.")
