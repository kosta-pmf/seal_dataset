#!/usr/bin/env python3
"""
Cleanup script to keep only MP4 files from extracted dataset
"""

import os
from pathlib import Path
from tqdm import tqdm

def remove_empty_dirs(directory):
    """Remove empty directories recursively"""
    directory = Path(directory)
    removed_dirs = []
    
    for dirpath, _, _ in os.walk(directory, topdown=False):
        dir_path = Path(dirpath)
        try:
            # Only remove if empty (no files and no subdirs)
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
                removed_dirs.append(dir_path)
        except OSError:
            print(f"Could not remove directory {dir_path}: {e}")
    
    return removed_dirs

def cleanup_extracted(extract_dir="extracted", dry_run=False, keep_extensions=None):
    """Remove all non-MP4 files from extracted directory"""
    
    if keep_extensions is None:
        keep_extensions = ['.mp4']
    
    keep_extensions = [ext.lower() for ext in keep_extensions]
    
    print(f"Scanning {extract_dir}...")
    extract_path = Path(extract_dir)
    
    if not extract_path.exists():
        print(f"Directory {extract_dir} does not exist")
        return
    
    keep_files = []
    remove_files = []
    
    for file_path in extract_path.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() in keep_extensions:
                keep_files.append(file_path)
            else:
                remove_files.append(file_path)
    
    print(f"Found {len(keep_files)} files to keep ({', '.join(keep_extensions)})")
    print(f"Found {len(remove_files)} files to remove")
    
    if not remove_files:
        print("No files to remove!")
        return
    
    if dry_run:
        print("=== DRY RUN - Files that would be removed: ===")
        for file_path in remove_files[:20]:  # Show first 20
            print(f"  {file_path}")
        if len(remove_files) > 20:
            print(f"  ... and {len(remove_files) - 20} more files")
        return
    
    total_size = sum(f.stat().st_size for f in remove_files)
    size_mb = total_size / (1024 * 1024)
    
    print(f"This will delete {len(remove_files)} files ({size_mb:.1f} MB)")
    confirm = input("Continue? (y/N): ").lower().strip()
    
    if confirm not in ['y', 'yes', '']:
        print("Cancelled")
        return
    
    print("Removing files...")
    removed_count = 0
    
    with tqdm(total=len(remove_files), desc="Removing files", unit="file") as pbar:
        for file_path in remove_files:
            try:
                file_path.unlink()
                removed_count += 1
            except OSError as e:
                print(f"Failed to remove {file_path}: {e}")
            pbar.update(1)
    
    print(f"Removed {removed_count}/{len(remove_files)} files")
    
    print("Removing empty directories...")
    removed_dirs = remove_empty_dirs(extract_path)
    if removed_dirs:
        print(f"Removed {len(removed_dirs)} empty directories")
    
    remaining_mp4s = list(extract_path.rglob("*.mp4"))
    print(f"Cleanup complete! {len(remaining_mp4s)} MP4 files remaining")

if __name__ == "__main__":
    cleanup_extracted("dataset")