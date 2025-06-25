#!/usr/bin/env python3
"""
Central dataset management script
Handles conversion, downloading, and extraction of dataset files
"""

import argparse
import sys
from pathlib import Path

# Import our modules
from convert_dataset_links import convert_tsv_to_formats
from download_dataset import download_dataset_file, download_multiple_files, list_available_files
from extract_dataset import extract_all_tars, extract_specific_files, get_tar_files
from cleanup_dataset import cleanup_extracted, show_summary

def setup_directories(downloads_dir, extract_dir):
    """Create necessary directories"""
    Path(downloads_dir).mkdir(exist_ok=True)
    Path(extract_dir).mkdir(exist_ok=True)

def convert_step(tsv_file):
    """Step 1: Convert TSV to JSON"""
    print("=== STEP 1: Converting TSV to JSON ===")
    if not Path(tsv_file).exists():
        print(f"Error: TSV file '{tsv_file}' not found")
        return False
    
    try:
        convert_tsv_to_formats(tsv_file)
        return True
    except Exception as e:
        print(f"Error converting TSV: {e}")
        return False

def download_step(files, downloads_dir):
    """Step 2: Download files"""
    print("=== STEP 2: Downloading Files ===")
    setup_directories(downloads_dir, "")
    
    if not Path("dataset_links.json").exists():
        print("Error: dataset_links.json not found. Run conversion step first.")
        return False
    
    try:
        if files == ["all"]:
            # Download all files
            available_files = list_available_files()
            print(f"Downloading all {len(available_files)} files...")
            results = download_multiple_files(available_files, downloads_dir)
        else:
            # Download specific files
            print(f"Downloading {len(files)} files...")
            results = download_multiple_files(files, downloads_dir)
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        print(f"\nDownload complete: {successful}/{total} files downloaded successfully")
        
        return successful > 0
    except Exception as e:
        print(f"Error during download: {e}")
        return False

def extract_step(files, downloads_dir, extract_dir):
    """Step 3: Extract files"""
    print("=== STEP 3: Extracting Files ===")
    setup_directories("", extract_dir)
    
    available_tars = get_tar_files(downloads_dir)
    if not available_tars:
        print(f"No tar files found in {downloads_dir}")
        return False
    
    try:
        if files == ["all"]:
            # Extract all tar files
            results = extract_all_tars(downloads_dir, extract_dir)
        else:
            # Extract specific files
            tar_files = [f for f in files if f.endswith('.tar')]
            if not tar_files:
                print("No .tar files specified for extraction")
                return False
            results = extract_specific_files(tar_files, downloads_dir, extract_dir)
        
        return any(results.values()) if results else False
    except Exception as e:
        print(f"Error during extraction: {e}")
        return False

def cleanup_step(extract_dir, keep_extensions, auto=False):
    """Step 4: Cleanup extracted files"""
    print("=== STEP 4: Cleaning up extracted files ===")
    
    try:
        if auto:
            import builtins
            original_input = builtins.input
            builtins.input = lambda _: 'y'
        
        cleanup_extracted(extract_dir, dry_run=False, keep_extensions=keep_extensions)
        
        if auto:
            builtins.input = original_input
        
        return True
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False

def list_step():
    """List available files"""
    print("=== Available Files ===")
    
    if Path("dataset_links.json").exists():
        files = list_available_files()
        print(f"Available for download: {len(files)} files")
        for i, f in enumerate(files[:10], 1):
            print(f"  {i}. {f}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
    else:
        print("No dataset_links.json found. Run conversion step first.")
    
    # List downloaded files
    downloads_path = Path("downloads")
    if downloads_path.exists():
        tar_files = list(downloads_path.glob("*.tar"))
        print(f"\nDownloaded: {len(tar_files)} files")
        for f in tar_files[:5]:
            print(f"  {f.name}")
        if len(tar_files) > 5:
            print(f"  ... and {len(tar_files) - 5} more files")
    
    # List extracted files
    extract_path = Path("extracted")
    if extract_path.exists():
        extracted = list(extract_path.iterdir())
        print(f"\nExtracted: {len(extracted)} items")
        show_summary("extracted")

def main():
    parser = argparse.ArgumentParser(
        description='Dataset Management Tool - Convert, Download, and Extract dataset files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline - convert, download all, extract all
  python dataset_manager.py --all
  
  # Just convert TSV to JSON
  python dataset_manager.py --convert
  
  # Download specific files
  python dataset_manager.py --download sav_000.tar sav_001.tar
  
  # Download and extract specific files
  python dataset_manager.py --download sav_000.tar --extract sav_000.tar
  
  # Full pipeline with cleanup
  python dataset_manager.py --all
  
  # Extract and cleanup
  python dataset_manager.py --extract --cleanup
  
  # Cleanup only (keep MP4s)
  python dataset_manager.py --cleanup
  
  # List available files
  python dataset_manager.py --list
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
                       help='Remove non-MP4 files from extracted directory')
    parser.add_argument('--list', action='store_true',
                       help='List available, downloaded, and extracted files')
    
    # Configuration
    parser.add_argument('--tsv-file', default='dataset links.txt',
                       help='Input TSV file (default: "dataset links.txt")')
    parser.add_argument('--downloads-dir', default='downloads',
                       help='Downloads directory (default: downloads)')
    parser.add_argument('--extract-dir', default='extracted',
                       help='Extraction directory (default: extracted)')
    parser.add_argument('--keep-extensions', nargs='+', default=['.mp4'],
                       help='File extensions to keep during cleanup (default: .mp4)')
    parser.add_argument('--auto-cleanup', action='store_true',
                       help='Skip confirmation prompt during cleanup')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    success = True
    
    # Handle --all flag
    if args.all:
        print("Running full pipeline...")
        success &= convert_step(args.tsv_file)
        if success:
            success &= download_step(["all"], args.downloads_dir)
        if success:
            success &= extract_step(["all"], args.downloads_dir, args.extract_dir)
        if success:
            success &= cleanup_step(args.extract_dir, args.keep_extensions, auto=True)
    else:
        # Handle individual steps
        if args.convert:
            success &= convert_step(args.tsv_file)
        
        if args.download is not None:
            files = args.download if args.download else ["all"]
            success &= download_step(files, args.downloads_dir)
        
        if args.extract is not None:
            files = args.extract if args.extract else ["all"]
            success &= extract_step(files, args.downloads_dir, args.extract_dir)
        
        if args.cleanup:
            success &= cleanup_step(args.extract_dir, args.keep_extensions, args.auto_cleanup)
    
    if args.list:
        list_step()
    
    if not success:
        print("\n❌ Some operations failed")
        sys.exit(1)
    else:
        print("\n✅ All operations completed successfully")

if __name__ == "__main__":
    main() 