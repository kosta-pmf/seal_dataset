#!/usr/bin/env python3
"""
Central dataset management script
Handles conversion, downloading, and extraction of dataset files
"""

import argparse
import sys
from pathlib import Path

from convert_dataset_links import convert_tsv_to_json   
from download_dataset import download_multiple_files, list_available_files
from extract_dataset import extract_all_tars, extract_specific_files, get_tar_files
from cleanup_dataset import cleanup_extracted

def setup_directories(downloads_dir, dataset_dir):
    """Create necessary directories"""
    Path(downloads_dir).mkdir(exist_ok=True)
    Path(dataset_dir).mkdir(exist_ok=True)

def convert_step(tsv_file):
    """Step 1: Convert TSV to JSON"""
    print("=== STEP 1: Converting TSV to JSON ===")
    if not Path(tsv_file).exists():
        print(f"Error: TSV file '{tsv_file}' not found")
        return False
    
    try:
        convert_tsv_to_json(tsv_file)
        return True
    except Exception as e:
        print(f"Error converting TSV: {e}")
        return False

def download_step(files, downloads_dir, max_files=None):
    """Step 2: Download files"""
    print("=== STEP 2: Downloading Files ===")
    setup_directories(downloads_dir, "")
    
    if not Path("dataset_links.json").exists():
        print("Error: dataset_links.json not found. Run conversion step first.")
        return False
    
    try:
        if files == ["all"]:
            available_files = list_available_files()
            if max_files and max_files < len(available_files):
                available_files = available_files[:max_files]
                print(f"Downloading first {len(available_files)} files (limited by --max-files)...")
            else:
                print(f"Downloading all {len(available_files)} files...")
            results = download_multiple_files(available_files, downloads_dir)
        else:
            print(f"Downloading {len(files)} files...")
            results = download_multiple_files(files, downloads_dir)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        print(f"Download complete: {successful}/{total} files downloaded successfully")
        
        return successful > 0
    except Exception as e:
        print(f"Error during download: {e}")
        return False

def extract_step(files, downloads_dir, dataset_dir):
    """Step 3: Extract files"""
    print("=== STEP 3: Extracting Files ===")
    setup_directories("", dataset_dir)
    
    available_tars = get_tar_files(downloads_dir)
    if not available_tars:
        print(f"No tar files found in {downloads_dir}")
        return False
    
    try:
        if files == ["all"]:
            results = extract_all_tars(downloads_dir, dataset_dir)
        else:
            tar_files = [f for f in files if f.endswith('.tar')]
            if not tar_files:
                print("No .tar files specified for extraction")
                return False
            results = extract_specific_files(tar_files, downloads_dir, dataset_dir)
        
        return any(results.values()) if results else False
    except Exception as e:
        print(f"Error during extraction: {e}")
        return False

def cleanup_step(dataset_dir, keep_extensions, auto=False):
    """Step 4: Cleanup extracted files"""
    print("=== STEP 4: Cleaning up extracted files ===")
    
    try:
        if auto:
            import builtins
            original_input = builtins.input
            builtins.input = lambda _: 'y'
        
        cleanup_extracted(dataset_dir, dry_run=False, keep_extensions=keep_extensions)
        
        if auto:
            builtins.input = original_input
        
        return True
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False

def show_summary(downloads_dir="downloads", dataset_dir="dataset"):
    """Show summary of pipeline status"""
    print("=== SUMMARY ===")

    # Check downloads
    downloads_path = Path(downloads_dir)
    if downloads_path.exists():
        tar_files = list(downloads_path.glob("*.tar"))
        print(f"Downloads: {len(tar_files)} files in {downloads_dir}/")
        if tar_files:
            total_size = sum(f.stat().st_size for f in tar_files)
            size_gb = total_size / (1024**3)
            print(f"    Total size: {size_gb:.2f} GB")
    else:
        print(f"Downloads: {downloads_dir}/ folder not found")
    
    # Check dataset
    dataset_path = Path(dataset_dir)
    if dataset_path.exists():
        # Count by extension
        extensions = {}
        total_files = 0
        total_size = 0
        
        for file_path in dataset_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower() or 'no extension'
                size = file_path.stat().st_size
                
                if ext not in extensions:
                    extensions[ext] = {'count': 0, 'size': 0}
                
                extensions[ext]['count'] += 1
                extensions[ext]['size'] += size
                total_files += 1
                total_size += size
        
        if total_files > 0:
            size_gb = total_size / (1024**3)
            print(f"Dataset: {total_files} files in {dataset_dir}/ ({size_gb:.2f} GB)")
            
            # Show top file types
            sorted_ext = sorted(extensions.items(), key=lambda x: x[1]['count'], reverse=True)
            for ext, data in sorted_ext[:5]:  # Show top 5
                count = data['count']
                size_mb = data['size'] / (1024**2)
                print(f"    {ext}: {count} files ({size_mb:.1f} MB)")
            
            if len(sorted_ext) > 5:
                print(f"    ... and {len(sorted_ext) - 5} more file types")
        else:
            print(f"Dataset: {dataset_dir}/ folder is empty")
    else:
        print(f"Dataset: {dataset_dir}/ folder not found")
    
    print()

def main():
    parser = argparse.ArgumentParser(
        description='Dataset Management Tool - Convert, Download, and Extract dataset files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline - convert, download all to downloads/, extract all to dataset/, cleanup
  python dataset_manager.py --all
  
  # Just convert TSV to JSON (creates dataset_links.json)
  python dataset_manager.py --convert
  
  # Download specific files to downloads/ folder
  python dataset_manager.py --download sav_000.tar sav_001.tar
  
  # Download and extract specific files (downloads/ -> dataset/)
  python dataset_manager.py --download sav_000.tar --extract sav_000.tar
  
  # Extract from downloads/ to dataset/ and cleanup (keep only MP4s)
  python dataset_manager.py --extract --cleanup
  
  # Cleanup only dataset/ folder (keep MP4s)
  python dataset_manager.py --cleanup
  
  # Custom folder paths
  python dataset_manager.py --all --downloads-dir my_downloads --dataset-dir my_dataset
  
  # Extract to custom folder and cleanup, keeping multiple file types
  python dataset_manager.py --extract --cleanup --dataset-dir videos --keep-extensions .mp4 .avi .mov
  
  # Download only first 5 files for testing
  python dataset_manager.py --download --max-files 5
  
  # Full pipeline but only process 10 files
  python dataset_manager.py --all --max-files 10
  
  # Show current status
  python dataset_manager.py --summary
        """
    )
    
    # Main actions
    parser.add_argument('--all', action='store_true', 
                       help='Run full pipeline: convert, download all, extract all')
    parser.add_argument('--convert', action='store_true',
                       help='Convert TSV file to JSON format')
    parser.add_argument('--download', nargs='*', metavar='FILE',
                       help='Download files (use "all" for all files)')
    parser.add_argument('--extract', nargs='*', metavar='FILE',
                       help='Extract tar files (use "all" for all files)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Remove non-MP4 files from dataset directory')
    parser.add_argument('--summary', action='store_true',
                       help='Show pipeline status summary')
    
    # Configuration
    parser.add_argument('--tsv-file', default='dataset links.txt',
                       help='Input TSV file (default: "dataset links.txt")')
    parser.add_argument('--downloads-dir', default='downloads',
                       help='Downloads directory (default: downloads)')
    parser.add_argument('--dataset-dir', default='dataset',
                       help='Dataset directory for extraction (default: dataset)')
    parser.add_argument('--keep-extensions', nargs='+', default=['.mp4'],
                       help='File extensions to keep during cleanup (default: .mp4)')
    parser.add_argument('--auto-cleanup', action='store_true',
                       help='Skip confirmation prompt during cleanup')
    parser.add_argument('--max-files', type=int, metavar='N',
                       help='Maximum number of files to download (useful for testing)')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    success = True
    
    if args.all:
        print("Running full pipeline...")
        success &= convert_step(args.tsv_file)
        if success:
            success &= download_step(["all"], args.downloads_dir, args.max_files)
        if success:
            success &= extract_step(["all"], args.downloads_dir, args.dataset_dir)
        if success:
            success &= cleanup_step(args.dataset_dir, args.keep_extensions, auto=True)
    else:
        # Handle individual steps
        if args.convert:
            success &= convert_step(args.tsv_file)
        
        if args.download is not None:
            files = args.download if args.download else ["all"]
            success &= download_step(files, args.downloads_dir, args.max_files)
        
        if args.extract is not None:
            files = args.extract if args.extract else ["all"]
            success &= extract_step(files, args.downloads_dir, args.dataset_dir)
        
        if args.cleanup:
            success &= cleanup_step(args.dataset_dir, args.keep_extensions, args.auto_cleanup)
    
    if args.summary:
        show_summary(args.downloads_dir, args.dataset_dir)
    
    if not success:
        print("Some operations failed")
        sys.exit(1)
    else:
        print("All operations completed successfully")

if __name__ == "__main__":
    main() 