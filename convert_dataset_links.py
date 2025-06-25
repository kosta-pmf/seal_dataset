"""
Script to convert dataset links TSV file to Python-friendly format
"""

import json
import csv
from pathlib import Path

def convert_tsv_to_json(input_file="dataset links.txt"):
    """Convert TSV file to JSON format"""
    
    dataset_links = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            dataset_links[row['file_name']] = row['cdn_link']
    
    with open('dataset_links.json', 'w', encoding='utf-8') as f:
        json.dump(dataset_links, f, indent=2)
    
    print(f"Converted {len(dataset_links)} entries")
    print("Created file:")
    print("- dataset_links.json (JSON format)")
    
    return dataset_links

if __name__ == "__main__":
    dataset_links = convert_tsv_to_json()
    
