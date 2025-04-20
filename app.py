# app.py
import json
import os
import sys
from urllib.parse import urlparse
import re # Import regex for filename sanitization

# --- Configuration ---
START_URL = "https://browser-use.com/"
URL_LIST_DIR = "url_lists" # Directory to store the URL list files
# --------------------

# --- Helper Function to Sanitize Filenames ---
def sanitize_filename(name):
    """Removes potentially problematic characters for filenames."""
    # Remove scheme if present (like http://)
    name = re.sub(r'^https?:\/\/', '', name)
    # Replace dots and slashes with underscores
    name = name.replace('.', '_').replace('/', '_')
    # Remove characters not suitable for filenames (allow letters, numbers, underscore, hyphen)
    name = re.sub(r'[^\w\-]+', '', name)
    # Ensure it's not empty
    return name or "default"
# ---------------------------------------------

# --- Derive Filename and Path ---
try:
    parsed_start_uri = urlparse(START_URL)
    # Use netloc (domain) for filename base, sanitized
    domain_part = parsed_start_uri.netloc if parsed_start_uri.netloc else "unknown_url"
    sanitized_domain = sanitize_filename(domain_part)
    url_filename = f"{sanitized_domain}_urls.jsonl"
    full_url_output_path = os.path.join(URL_LIST_DIR, url_filename)
except Exception as e:
    print(f"Error parsing START_URL '{START_URL}' to generate filename: {e}")
    sys.exit(1)
# ---------------------------------

# --- Step 1: Run the URL Finder ---
print("--- Running URL Finder ---")
try:
    from run_url_finder import run_spider
except ImportError:
    print("Error: Could not import 'run_spider' from 'run_url_finder.py'.")
    print("Ensure 'run_url_finder.py' is in the same directory.")
    sys.exit(1)

try:
    # Pass the full path to the run_spider function
    run_spider(start_url=START_URL, output_file_path=full_url_output_path) # Domain auto-derived
    print(f"--- URL Finder finished. URLs should be in {full_url_output_path} ---")
except Exception as e:
    print(f"\nError occurred during URL finding: {e}")
    sys.exit(1)

# --- Step 2: Extract Content from Found URLs ---
print(f"\n--- Starting Content Extraction from {full_url_output_path} ---")

# Import necessary components for extraction
try:
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
         sys.path.insert(0, project_dir)
    from utils.WebpageExtractor import WebpageExtractor
    from utils.FileSaver import write_to_markdown
except ImportError as e:
     print(f"Error: Could not import required modules from 'utils': {e}")
     print("Ensure 'utils' directory with necessary files exists.")
     sys.exit(1)

# Check if the URL file exists *at the expected full path*
if not os.path.exists(full_url_output_path):
    print(f"Error: Output file '{full_url_output_path}' not found. URL Finder might have failed or saved elsewhere.")
    sys.exit(1)

# --- Read URLs from the file at the full path ---
target_urls: list = []
try:
    with open(full_url_output_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                url = data["url"]
                target_urls.append(url)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Skipping invalid line in {full_url_output_path}: {line.strip()} - Error: {e}")
                continue
except Exception as e:
     print(f"Error reading {full_url_output_path}: {e}")
     sys.exit(1)

# --- Process the extracted URLs (logic remains the same) ---
if target_urls:
    print(f"Processing {len(target_urls)} URLs from {full_url_output_path}...")
    extractor = WebpageExtractor()

    for i, link in enumerate(target_urls):
        print(f"Processing: {link}")
        result = extractor.extract(link)

        try:
            parsed_uri = urlparse(link)
            domain_name = parsed_uri.netloc if parsed_uri.netloc else "unknown_domain"
            url_path_basename = os.path.basename(parsed_uri.path)

            if not url_path_basename or url_path_basename == '/':
                filename_base = "index"
            else:
                filename_base, _ = os.path.splitext(url_path_basename)

            if not filename_base:
                 filename_base = f"page_{i+1}"
            output_filename_base = f"{filename_base}.md"

        except Exception as e:
            print(f"Warning: Error parsing URL '{link}' for filename generation: {e}")
            domain_name = "parsing_error_domain"
            output_filename_base = f"error_site_{i+1}.md"

        write_to_markdown(result, output_filename_base, domain=domain_name)

    print("--- Content Extraction finished. ---")
else:
    print(f"No valid URLs found or loaded from {full_url_output_path}.")

print("\n--- app.py finished ---")