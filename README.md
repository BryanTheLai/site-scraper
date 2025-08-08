<div align="center">

# 🕷️ site-scraper

**Universal Site Crawler ➔ Content Extractor ➔ Markdown Publisher**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![Scrapy](https://img.shields.io/badge/Scrapy-2.12.0-green.svg)](https://scrapy.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

_A minimal, high-performance CLI to crawl any website, extract main content, and publish Markdown_ 

</div>

---

## 🚀 Overview

At its core, **site-scraper** leverages first principles:
1. **Crawl Graph:** Discover every node (URL) in a domain via breadth-first link traversal.
2. **Extract Substance:** Isolate title & main body text using a proven content extraction library (trafilatura).
3. **Serialize Output:** Persist structured artifacts—JSONL of URLs, and Markdown files with YAML front-matter.

Everything is orchestrated in under 200 lines of Python, with zero external orchestration required.

---

## 🔑 Key Features

- **🔎 Universal Crawling:** Handles relative links, subdomains, robots.txt, and redirect chains.
- **⚡ High Throughput:** Concurrent requests, auto-throttle, and depth control for scalable performance.
- **📄 Clean Markdown:** YAML front-matter (`site_url`, `title`) plus extracted content in Markdown.
- **⚙️ Configurable:** Tweak crawl settings (`DOWNLOAD_DELAY`, `CONCURRENT_REQUESTS`), extraction options, and output paths via code.

---

## 🛠️ Quick Start

```bash
# 1. Clone & install
git clone https://github.com/BryanTheLai/site-scraper.git
cd site-scraper
python -m venv venv; source venv/bin/activate  # Windows PowerShell: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Crawl and list URLs
python src/run_url_finder.py https://example.com -o example_urls.jsonl

# 3. Extract and publish Markdown
python src/app.py
```

---

## 📂 Examples

### First lines of `url_lists/example_urls.jsonl`
```json
{"url": "https://example.com/"}
{"url": "https://example.com/about/"}
{"url": "https://example.com/blog/"}
```

### Sample Markdown: `output_folder/example.com/about.md`
```markdown
---
site_url: "https://example.com/about/"
title: "About Us — Example.com"
---

Example Inc. is a hypothetical company dedicated to showcasing best practices in README design...
```

---

## 🗂️ Project Structure

```text
.
├── src/
│   ├── find_urls.py          # Scrapy spider definition
│   ├── run_url_finder.py     # CLI entrypoint for crawling
│   ├── app.py                # Orchestrates crawling + extraction
│   └── utils/
│       ├── WebpageExtractor.py  # Fetch & extract HTML → Markdown
│       └── FileSaver.py         # Persist output to disk
├── url_lists/               # JSONL files of discovered URLs
├── output_folder/           # Markdown output organized by domain
├── requirements.txt         # Pinned dependencies
└── README.md                # You are reading it
```
