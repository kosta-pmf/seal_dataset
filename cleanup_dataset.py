#!/usr/bin/env python3
"""
Cleanup script to keep only MP4 files from extracted dataset
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm
import argparse

def scan_files(directory):
    """Scan directory and categorize files"""
    directory = Path(directory)
    if not directory.exists():
        return [], []
    
    mp4_files = []
    other_files = []
    
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() == '.mp4':
                mp4_files.append(file_path)
            else:
                other_files.append(file_path)
    
    return mp4_files, other_files

def remove_empty_dirs(directory):
    """Remove empty directories recursively"""
    directory = Path(directory)
    removed_dirs = []
    
    # Walk from bottom up to handle nested empty dirs
    for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
        dir_path = Path(dirpath)
        try:
            # Only remove if empty (no files and no subdirs)
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
                removed_dirs.append(dir_path)
        except OSError:
            # Directory not empty or permission error
            pass
    
    return removed_dirs

def cleanup_extracted(extract_dir="extracted", dry_run=False, keep_extensions=None):
    """Remove all non-MP4 files from extracted directory"""
    
    if keep_extensions is None:
        keep_extensions = ['.mp4']
    
    # Normalize extensions to lowercase
    keep_extensions = [ext.lower() for ext in keep_extensions]
    
    print(f"Scanning {extract_dir}...")
    extract_path = Path(extract_dir)
    
    if not extract_path.exists():
        print(f"Directory {extract_dir} does not exist")
        return
    
    # Scan all files
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
        print("\n=== DRY RUN - Files that would be removed: ===")
        for file_path in remove_files[:20]:  # Show first 20
            print(f"  {file_path}")
        if len(remove_files) > 20:
            print(f"  ... and {len(remove_files) - 20} more files")
        return
    
    # Confirm deletion
    total_size = sum(f.stat().st_size for f in remove_files)
    size_mb = total_size / (1024 * 1024)
    
    print(f"\nThis will delete {len(remove_files)} files ({size_mb:.1f} MB)")
    confirm = input("Continue? (y/N): ").lower().strip()
    
    if confirm not in ['y', 'yes']:
        print("Cancelled")
        return
    
    # Remove files with progress bar
    print("\nRemoving files...")
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
    
    # Remove empty directories
    print("Removing empty directories...")
    removed_dirs = remove_empty_dirs(extract_path)
    if removed_dirs:
        print(f"Removed {len(removed_dirs)} empty directories")
    
    # Final summary
    remaining_mp4s = list(extract_path.rglob("*.mp4"))
    print(f"\n✅ Cleanup complete! {len(remaining_mp4s)} MP4 files remaining")

def show_summary(extract_dir="extracted"):
    """Show summary of files in extracted directory"""
    extract_path = Path(extract_dir)
    
    if not extract_path.exists():
        print(f"Directory {extract_dir} does not exist")
        return
    
    # Count by extension
    extensions = {}
    total_size = 0
    
    for file_path in extract_path.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower() or 'no extension'
            size = file_path.stat().st_size
            
            if ext not in extensions:
                extensions[ext] = {'count': 0, 'size': 0}
            
            extensions[ext]['count'] += 1
            extensions[ext]['size'] += size
            total_size += size
    
    print(f"\n=== Files in {extract_dir} ===")
    print(f"Total: {sum(ext['count'] for ext in extensions.values())} files, {total_size/(1024*1024):.1f} MB")
    
    for ext, data in sorted(extensions.items(), key=lambda x: x[1]['count'], reverse=True):
        size_mb = data['size'] / (1024 * 1024)
        print(f"  {ext}: {data['count']} files ({size_mb:.1f} MB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cleanup extracted files - keep only MP4s')
    
    parser.add_argument('--dir', default='extracted', help='Extracted directory to clean')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed without deleting')
    parser.add_argument('--summary', action='store_true', help='Show file summary without cleaning')
    parser.add_argument('--keep', nargs='+', default=['.mp4'], 
                       help='File extensions to keep (default: .mp4)')
    parser.add_argument('--auto', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if args.summary:
        show_summary(args.dir)
    else:
        # Override confirmation if auto mode
        if args.auto:
            import builtins
            original_input = builtins.input
            builtins.input = lambda _: 'y'
        
        cleanup_extracted(args.dir, args.dry_run, args.keep)
        
        if args.auto:
            builtins.input = original_input 