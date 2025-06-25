#!/usr/bin/env python3
"""
Dataset extraction utility
"""

import tarfile
import os
from pathlib import Path
from tqdm import tqdm
import json

def get_tar_files(directory="downloads"):
    """Get all tar files in the specified directory"""
    tar_files = []
    path = Path(directory)
    if path.exists():
        tar_files = list(path.glob("*.tar"))
    return tar_files

def extract_tar_with_progress(tar_path, extract_to="dataset"):
    """Extract a tar file with progress bar"""
    extract_path = Path(extract_to)
    extract_path.mkdir(exist_ok=True)
    
    tar_name = tar_path.name
    print(f"Extracting {tar_name}...")
    
    with tarfile.open(tar_path, 'r') as tar:
        members = tar.getmembers()
        
        with tqdm(total=len(members), desc=tar_name, unit='file') as pbar:
            for member in members:
                tar.extract(member, path=extract_path)
                pbar.update(1)
    
    print(f"Extracted {tar_name} to {extract_path}")
    return True

def extract_all_tars(downloads_dir="downloads", extract_to="dataset"):
    """Extract all tar files in downloads directory"""
    tar_files = get_tar_files(downloads_dir)
    
    if not tar_files:
        print(f"No tar files found in {downloads_dir}")
        return
    
    print(f"Found {len(tar_files)} tar files")
    
    results = {}
    for tar_file in tar_files:
        try:
            extract_tar_with_progress(tar_file, extract_to)
            results[tar_file.name] = True
        except Exception as e:
            print(f"Failed to extract {tar_file.name}: {e}")
            results[tar_file.name] = False
    
    # Summary
    successful = sum(1 for success in results.values() if success)
    print(f"\nExtraction complete: {successful}/{len(tar_files)} files extracted successfully")
    
    return results

def extract_specific_files(filenames, downloads_dir="downloads", extract_to="dataset"):
    """Extract specific tar files by name"""
    results = {}
    
    for filename in filenames:
        tar_path = Path(downloads_dir) / filename
        
        if not tar_path.exists():
            print(f"File not found: {filename}")
            results[filename] = False
            continue
        
        try:
            extract_tar_with_progress(tar_path, extract_to)
            results[filename] = True
        except Exception as e:
            print(f"Failed to extract {filename}: {e}")
            results[filename] = False
    
    return results

def list_tar_contents(tar_path):
    """List contents of a tar file without extracting"""
    with tarfile.open(tar_path, 'r') as tar:
        members = tar.getmembers()
        print(f"\nContents of {tar_path.name}:")
        for member in members[:10]:  # Show first 10 files
            print(f"  {member.name}")
        if len(members) > 10:
            print(f"  ... and {len(members) - 10} more files")

if __name__ == "__main__":
    extract_all_tars("downloads", "dataset")
    