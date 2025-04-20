import json
import requests
import trafilatura
import lxml.html
from typing import Optional, Dict, Any

class WebpageExtractor:
    """Fetches and extracts main content from a webpage URL."""

    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    DEFAULT_TRAFILATURA_CONFIG = {
        "favor_precision": False,
        "favor_recall": True,
        "include_comments": False,
        "include_tables": True,
        "include_images": False,
        "include_formatting": True, # Keep false for cleaner Markdown usually
        "include_links": False,
        "output_format": 'markdown', # Set to markdown
        "deduplicate": True,
    }

    def __init__(self, headers: Optional[Dict[str, str]] = None,
                 trafilatura_config: Optional[Dict[str, Any]] = None):
        """Initializes the extractor."""
        self.headers = headers or self.DEFAULT_HEADERS
        self.config = trafilatura_config or self.DEFAULT_TRAFILATURA_CONFIG

    def _fetch(self, url: str) -> Optional[str]:
        """Fetches HTML content."""
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException:
            return None

    def _get_title(self, html_content: str) -> Optional[str]:
        """Extracts the title."""
        if not html_content:
            return None
        try:
            root = lxml.html.fromstring(html_content)
            title = root.findtext('.//title')
            return title.strip() if title else None
        except Exception:
            return None

    def extract(self, url: str) -> Dict[str, Optional[str]]:
        """Fetches, extracts title and main content."""
        html_content = self._fetch(url)
        title = self._get_title(html_content)

        if not html_content:
            return {'url': url, 'title': title, 'content': None}

        extracted_content = None
        try:
            extracted_content = trafilatura.extract(
                html_content,
                url=url,
                **self.config
            )
        except Exception:
            pass

        return {'url': url, 'title': title, 'content': extracted_content}

# src/utils/WebpageExtractor.py
# ... (class definition remains the same) ...

# --- Example Usage (if run directly) ---
if __name__ == "__main__":
    import json
    import os
    import sys
    from urllib.parse import urlparse

    # --- Setup Project Path ---
    # Get the directory containing the 'src' directory (project root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Add the project root to the Python path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # --------------------------

    # --- Imports relative to project root ---
    try:
        # Import FileSaver using its new path
        from src.utils.FileSaver import write_to_markdown
    except ImportError:
        print("Error: Could not import write_to_markdown from src.utils.FileSaver")
        sys.exit(1)
    # --------------------------------------

    # Define directories relative to project root
    URL_LIST_DIR_NAME = "url_lists"
    # ---

    # Construct absolute path to input file
    INPUT_JSONL_FILENAME = "aider_urls.jsonl" # Example filename
    input_jsonl_path = os.path.join(project_root, URL_LIST_DIR_NAME, INPUT_JSONL_FILENAME)

    target_urls: list = []
    if not os.path.exists(input_jsonl_path):
        print(f"Error: Input file not found: {input_jsonl_path}")
        sys.exit(1)

    try:
        with open(input_jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    url = data["url"]
                    target_urls.append(url)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Skipping invalid line in {input_jsonl_path}: {line.strip()} - Error: {e}")
                    continue
    except Exception as e:
        print(f"Error reading {input_jsonl_path}: {e}")
        sys.exit(1)

    if target_urls:
        print(f"Processing {len(target_urls)} URLs from {input_jsonl_path}...")
        # Instantiate the class itself
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

            # write_to_markdown is imported from src.utils.FileSaver
            # It will handle placing files correctly relative to project root
            write_to_markdown(result, output_filename_base, domain=domain_name)
        print("Finished processing.")
    else:
        print(f"No valid URLs found or loaded from {input_jsonl_path}.")