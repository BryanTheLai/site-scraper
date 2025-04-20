# run_url_finder.py
import argparse
import sys
from urllib.parse import urlparse
import os

# Define the directory for URL list files
URL_LIST_DIR = "url_lists"

# Add the project directory to the Python path to find 'find_urls' module
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

try:
    from find_urls import UrlFinderSpider
except ImportError:
    print("Error: Could not import UrlFinderSpider from find_urls.py")
    sys.exit(1)

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings # Although not used directly, good practice

def run_spider(start_url, output_file_path, domain=None): # Takes full path now
    """Configures and runs the UrlFinderSpider."""

    # --- Ensure output directory exists ---
    output_dir = os.path.dirname(output_file_path)
    if output_dir: # Only create if path includes a directory
        os.makedirs(output_dir, exist_ok=True)
    # ------------------------------------

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
        output_file_path: { # Use the full path here
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
    print(f"Output will be saved to '{output_file_path}'") # Show the full path
    process.crawl(UrlFinderSpider, start_url=start_url, domain=domain)
    process.start() # Blocks until finished
    print("Crawling finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Find all unique URLs within a domain using Scrapy. Saves output to '{URL_LIST_DIR}/' directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "start_url",
        help="The full starting URL (e.g., 'https://www.example.com')"
    )
    parser.add_argument(
        "-o", "--output",
        default="found_urls.jsonl",
        # Help text clarifies it's just the filename now
        help=f"Filename for the output file (will be placed in '{URL_LIST_DIR}/')."
    )
    parser.add_argument(
        "-d", "--domain",
        default=None,
        help="Optional: The domain to restrict the crawl to (e.g., 'example.com'). If not provided, it will be derived from the start_url."
    )

    args = parser.parse_args()

    # Construct the full path when run standalone
    full_output_path = os.path.join(URL_LIST_DIR, args.output)

    run_spider(args.start_url, full_output_path, args.domain)