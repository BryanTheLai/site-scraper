import os

def write_to_markdown(result, filename, domain: str = "no_domain"):
    # domain for example aider.com
    # so the saved file should be output_folder/aider.com/extracted_site_i.md
    base_output_dir = "output_folder"
    # Sanitize domain name slightly for folder usage (optional, but good practice)
    # Replace potential problematic characters if needed, but netloc is usually safe
    safe_domain_folder = domain if domain else "unknown_domain"

    # Create the full path including the domain subfolder
    domain_output_dir = os.path.join(base_output_dir, safe_domain_folder)
    os.makedirs(domain_output_dir, exist_ok=True)  # Ensure the domain folder exists

    # Construct the final file path within the domain subfolder
    output_filepath = os.path.join(domain_output_dir, os.path.basename(filename))

    if result['content']:
        markdown_content = f"""---
site_url: "{result['url']}"
title: "{result['title'] or 'Not Found'}"
---

{result['content']}
"""
        try:
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"\nSaved output to {output_filepath}")
        except IOError:
            print(f"Error: Could not save file {output_filepath}")
    else:
        print("Failed to fetch or extract any information from the URL.")