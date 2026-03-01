import json
import os
import glob

all_data = []

# This looks for ANY .txt file in the same folder as the script
files = glob.glob("*.txt")

if not files:
    print("Error: I still can't see any .txt files. Are they in this folder?")
    print(f"Current Directory: {os.getcwd()}")
else:
    for filename in files:
        print(f"Reading {filename}...")
        # 'latin-1' or 'utf-8' with ignore handles weird RTF-to-TXT artifacts
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            # Splitting by double newline to keep paragraphs as searchable units
            paragraphs = f.read().split('\n\n')
            for p in paragraphs:
                clean_p = p.strip()
                if clean_p:
                    all_data.append({
                        "title": filename.replace(".txt", "").upper(),
                        "text": clean_p
                    })

    # Save the data.js file
    with open('data.js', 'w', encoding='utf-8') as out:
        out.write("const nabokovWorks = " + json.dumps(all_data) + ";")

    print(f"\nSuccess! Created data.js with {len(all_data)} entries.")
    print("Now open your index.html file to search.")