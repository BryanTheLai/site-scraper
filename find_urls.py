# find_urls.py

import scrapy
from urllib.parse import urlparse

class UrlFinderSpider(scrapy.Spider):
    name = 'url_finder'

    def __init__(self, start_url=None, domain=None, *args, **kwargs):
        if not start_url or not domain:
            raise ValueError("Both 'start_url' and 'domain' arguments are required.")
        self.start_urls = [start_url]
        self.allowed_domains = [domain]
        self.found_urls = set()
        super().__init__(*args, **kwargs)
        self.log(f"Starting crawl at: {start_url} within domain: {domain}")

    def parse(self, response):
        current_url = response.url

        # --- Yield the current URL if it's valid and new ---
        # Extract the netloc (domain) from the current URL
        # Use response.url as it's the final URL after redirects
        current_netloc = urlparse(response.url).netloc
        # Handle www. prefix for comparison if needed, though allowed_domains should suffice
        current_domain_base = current_netloc.replace('www.', '')

        # Check if the final URL's domain matches our allowed domain
        # This is a stricter check than just allowed_domains which might allow subdomains
        # if the base domain was given. Adjust if you *want* all subdomains.
        # For simplicity here, let's trust allowed_domains primarily, but add the found_urls check.
        # Re-evaluate domain check if needed. Let's assume allowed_domains handles it.
        if response.url not in self.found_urls:
             # Check if the response URL domain is within the allowed list
             # This handles cases where allowed_domains = ['example.com'] and
             # we land on www.example.com or docs.example.com.
             # urlparse(response.url).netloc provides the full domain including subdomains.
             is_allowed = False
             response_domain = urlparse(response.url).netloc
             for allowed_domain in self.allowed_domains:
                 # Check if response domain is exactly the allowed domain or a subdomain of it
                 if response_domain == allowed_domain or response_domain.endswith('.' + allowed_domain):
                     is_allowed = True
                     break

             if is_allowed:
                 self.found_urls.add(response.url)
                 yield {'url': response.url}
             #else: # Optional: log if a URL was visited but not yielded due to domain mismatch after redirect
             #    self.log(f"Skipping yield for {response.url} - outside allowed domain(s) {self.allowed_domains}", level=scrapy.log.INFO)


        # --- Find and follow valid links ---
        links = response.css('a::attr(href)').getall()
        # self.log(f"Found {len(links)} links on {current_url}") # Reduced logging verbosity

        for link in links:
            # Basic check to filter out non-web links BEFORE calling follow
            if link and not link.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                try:
                    # Use response.follow - it handles relative URLs, allowed_domains check,
                    # and duplicate request filtering automatically.
                    yield response.follow(link, callback=self.parse)
                except Exception as e:
                    # Log errors during follow generation if needed, but Scrapy usually handles internal errors
                    self.log(f"Error trying to follow link '{link}' from {response.url}: {e}", level=scrapy.log.ERROR)
            # else: # Optional: log skipped links
            #    if link and link.startswith('#'):
            #        pass # Skip logging fragment links silently
            #    else:
            #        self.log(f"Skipping non-web link: {link}", level=scrapy.log.DEBUG)

    def closed(self, reason):
        self.log(f"Spider finished: {reason}. Found {len(self.found_urls)} unique internal URLs yielded.")