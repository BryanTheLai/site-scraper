# src/utils/FileSaver.py
import os
import sys

# --- Setup Project Path ---
# Get the directory containing the 'src' directory (project root)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add the project root to the Python path if needed (though usually called by app.py which does this)
# if project_root not in sys.path:
#    sys.path.insert(0, project_root) # Generally not needed here if app.py sets it up
# --------------------------

# Define output directory name relative to project root
BASE_OUTPUT_DIR_NAME = "output_folder"

def write_to_markdown(result, filename, domain: str = "unknown_domain"):
    """
    Writes the extraction result to a Markdown file within a domain-specific subfolder
    located in the project root's output directory.

    Args:
        result: Dictionary containing 'url', 'title', 'content'.
        filename: The base name for the output file (e.g., "extracted_site_1.md").
        domain: The domain name used to create a subfolder (e.g., "aider.chat").
    """
    # Construct the absolute path to the base output directory in the project root
    base_output_dir_abs = os.path.join(project_root, BASE_OUTPUT_DIR_NAME)

    safe_domain_folder = domain if domain else "unknown_domain"

    # Create the full path including the domain subfolder within the absolute base dir
    domain_output_dir = os.path.join(base_output_dir_abs, safe_domain_folder)
    try:
        os.makedirs(domain_output_dir, exist_ok=True) # Ensure the domain folder exists
    except OSError as e:
        print(f"Error creating directory {domain_output_dir}: {e}")
        return # Stop if we can't create the directory

    # Construct the final absolute file path within the domain subfolder
    output_filepath = os.path.join(domain_output_dir, os.path.basename(filename))

    if result and result.get('content'):
        markdown_content = f"""---
site_url: "{result.get('url', 'N/A')}"
title: "{result.get('title', 'Not Found')}"
---

{result['content']}
"""
        try:
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"Saved output to {output_filepath}") # Use the absolute path
        except IOError as e:
            print(f"Error: Could not save file {output_filepath}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing {output_filepath}: {e}")
    elif result:
         print(f"No content extracted for URL: {result.get('url', 'N/A')}. Skipping file save.")
    else:
        print("Error: Invalid result object passed. Skipping file save.")