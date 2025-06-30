# Dataset Manager

A Python CLI tool for managing SA-V dataset for video watermarking - converts links, downloads files, extracts archives, and cleans up to keep only MP4s.

## Features

- **Convert** TSV link files to JSON format
- **Download** files with progress bars and size limits
- **Extract** tar archives to organized folders
- **Cleanup** non-MP4 files automatically
- **Summary** status reporting
-**Pipeline** mode for full automation

## Quick Start

1. **Setup**
   ```bash
   python -m venv venv
   venv\Scripts\Activate.ps1  # Windows
   pip install -r requirements.txt
   ```

2. **Full Pipeline** (convert, download all, extract, cleanup)
   ```bash
   python dataset_manager.py --all
   ```

3. **Test with Limited Files**
   ```bash
   python dataset_manager.py --all --max-files 5
   ```

## Usage Examples

```bash
# Convert TSV to JSON
python dataset_manager.py --convert

# Download specific files
python dataset_manager.py --download sav_000.tar sav_001.tar

# Download with file limit
python dataset_manager.py --download --max-files 10

# Extract and cleanup
python dataset_manager.py --extract --cleanup

# Check status
python dataset_manager.py --summary

# Custom directories
python dataset_manager.py --all --downloads-dir my_downloads --dataset-dir my_videos
```

## File Structure

```
project/
├── dataset links.txt          # Input TSV file
├── dataset_links.json         # Converted links
├── downloads/                 # Downloaded tar files
├── dataset/                   # Extracted MP4 files
└── requirements.txt          # Dependencies
```

## Options

- `--max-files N` - Limit downloads for testing
- `--auto-cleanup` - Skip cleanup confirmation
- `--keep-extensions` - Specify file types to keep
- `--downloads-dir` / `--dataset-dir` - Custom folders

## Requirements

- Python 3.7+
- `requests` - For downloading
- `tqdm` - For progress bars

Run `pip install -r requirements.txt` to install dependencies. 