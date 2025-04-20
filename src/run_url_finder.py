# src/run_url_finder.py
import argparse
import sys
from urllib.parse import urlparse
import os

# --- Setup Project Path ---
# Get the directory containing the 'src' directory (project root)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the project root to the Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------

# --- Constants ---
# Define directory name relative to project root
URL_LIST_DIR_NAME = "url_lists"
# --- End Constants ---


# --- Imports relative to project root ---
try:
    # Import find_urls now relative to src
    from src.find_urls import UrlFinderSpider
except ImportError:
    print("Error: Could not import UrlFinderSpider from src.find_urls.py")
    sys.exit(1)

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
# --------------------------------------


def run_spider(start_url, output_file_path, domain=None): # Takes absolute path
    """Configures and runs the UrlFinderSpider."""

    # Ensure output directory exists (using the absolute path provided)
    output_dir = os.path.dirname(output_file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # --- Configuration ---
    if domain is None:
        try:
            parsed_uri = urlparse(start_url)
            domain = parsed_uri.netloc.replace('www.', '')
            if not domain:
                 raise ValueError("Could not parse domain")
            print(f"Automatically derived domain: {domain}")
        except Exception as e:
             print(f"Error: Could not automatically determine domain from {start_url}: {e}")
             sys.exit(1)

    settings = Settings()
    # Standard Scrapy settings...
    settings['USER_AGENT'] = 'MyUrlFinderBot/1.0 (+http://mydomain.com/botinfo)'
    settings['ROBOTSTXT_OBEY'] = True
    settings['LOG_LEVEL'] = 'INFO'
    settings['COOKIES_ENABLED'] = False
    settings['DOWNLOAD_DELAY'] = 0.5
    settings['AUTOTHROTTLE_ENABLED'] = True
    settings['DEPTH_LIMIT'] = 0
    settings['CONCURRENT_REQUESTS'] = 8
    settings['CONCURRENT_REQUESTS_PER_DOMAIN'] = 4
    settings['FEEDS'] = {
        output_file_path: { # Use the absolute path here
            'format': 'jsonlines',
            'encoding': 'utf8',
            'store_empty': False,
            'overwrite': True,
            'fields': ['url'],
            'indent': 0,
        }
    }

    # --- Run the Crawler ---
    process = CrawlerProcess(settings)
    print(f"Starting crawl for domain '{domain}' at '{start_url}'...")
    print(f"Output will be saved to '{output_file_path}'") # Show the absolute path
    # Pass the spider class directly (imported from src.find_urls)
    process.crawl(UrlFinderSpider, start_url=start_url, domain=domain)
    process.start() # Blocks until finished
    print("Crawling finished.")

# --- Main execution block (if run directly) ---
if __name__ == "__main__":
    # This part is mainly for standalone testing of this script,
    # app.py is the intended entry point.
    parser = argparse.ArgumentParser(
        description=f"Find URLs. Saves output to '{URL_LIST_DIR_NAME}/' relative to project root.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "start_url",
        help="The full starting URL (e.g., 'https://www.example.com')"
    )
    parser.add_argument(
        "-o", "--output",
        default="found_urls.jsonl",
        help=f"Filename for the output file (will be placed in '{URL_LIST_DIR_NAME}/')."
    )
    parser.add_argument(
        "-d", "--domain",
        default=None,
        help="Optional: Domain restriction (e.g., 'example.com'). Auto-derived if None."
    )

    args = parser.parse_args()

    # Construct the absolute path when run standalone
    # Assumes run from project root or src, calculates root path correctly
    abs_url_list_dir = os.path.join(project_root, URL_LIST_DIR_NAME)
    full_output_path = os.path.join(abs_url_list_dir, args.output)

    run_spider(args.start_url, full_output_path, args.domain)