"""
Dataset downloader utility
"""

import requests
from pathlib import Path
import json
from tqdm import tqdm
from convert_dataset_links import convert_tsv_to_json

def load_dataset_links(json_file="dataset_links.json"):
    """Load dataset links from JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def download_dataset_file(filename, output_dir="downloads", links_file="dataset_links.json"):
    """Download a specific dataset file"""
    Path(output_dir).mkdir(exist_ok=True)
    
    dataset_links = load_dataset_links(links_file)
    
    if filename not in dataset_links:
        print(f"File {filename} not found in dataset")
        return False
    
    url = dataset_links[filename]
    output_path = Path(output_dir) / filename
    
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"Downloaded to {output_path}")
        return True
    else:
        print(f"Failed to download {filename}: {response.status_code}")
        return False

def download_multiple_files(filenames, output_dir="downloads", links_file="dataset_links.json"):
    """Download multiple dataset files"""
    results = {}
    for filename in filenames:
        results[filename] = download_dataset_file(filename, output_dir, links_file)
    return results

def list_available_files(links_file="dataset_links.json"):
    """List all available files in the dataset"""
    dataset_links = load_dataset_links(links_file)
    return list(dataset_links.keys())

if __name__ == "__main__":
    convert_tsv_to_json()
    files = list_available_files()
    print(f"Available files: {len(files)}")
    for f in files[:5]:  # Show first 5
        print(f"  {f}")
    print("...")
    
    download_dataset_file(files[0]) 