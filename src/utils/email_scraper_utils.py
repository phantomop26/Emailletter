"""
Email Scraping Utilities
Multiple methods for extracting emails from websites
"""

import re
import requests
import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from typing import List, Set
import time

# Email regex pattern
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

async def scrape_emails_playwright(url: str, timeout: int = 15000) -> List[str]:
    """Scrape emails using Playwright (handles JavaScript)"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set user agent to avoid blocking
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            await page.goto(url, timeout=timeout, wait_until='networkidle')
            content = await page.content()
            await browser.close()
            
            emails = re.findall(EMAIL_REGEX, content)
            return list(set(emails))  # Remove duplicates
            
    except Exception as e:
        print(f"Playwright error for {url}: {e}")
        return []

def scrape_emails_requests(url: str) -> List[str]:
    """Fallback: Scrape emails using requests (faster, but no JavaScript)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        emails = re.findall(EMAIL_REGEX, response.text)
        return list(set(emails))
        
    except Exception as e:
        print(f"Requests error for {url}: {e}")
        return []

async def scrape_emails_hybrid(url: str) -> List[str]:
    """
    Hybrid approach: Try Playwright first, fallback to requests
    Returns the best result from both methods
    """
    # Handle NaN, None, or empty values
    if not url or str(url).lower() in ['nan', 'none', ''] or url is None:
        return []
    
    # Convert to string in case it's not already
    url = str(url).strip()
    
    # Clean URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"🔍 Scraping {url}...")
    
    all_emails: Set[str] = set()
    
    # Method 1: Try Playwright (handles JavaScript)
    try:
        playwright_emails = await scrape_emails_playwright(url)
        all_emails.update(playwright_emails)
        print(f"  📧 Playwright found: {len(playwright_emails)} emails")
    except Exception as e:
        print(f"  ❌ Playwright failed: {e}")
    
    # Method 2: Try requests as fallback
    try:
        requests_emails = scrape_emails_requests(url)
        all_emails.update(requests_emails)
        print(f"  📧 Requests found: {len(requests_emails)} emails")
    except Exception as e:
        print(f"  ❌ Requests failed: {e}")
    
    # Filter out common non-email patterns
    filtered_emails = []
    for email in all_emails:
        email_lower = email.lower()
        # Skip common false positives
        if not any(skip in email_lower for skip in [
            'image', 'photo', 'logo', 'icon', 'banner', 'placeholder',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp',
            'example.com', 'domain.com', 'yoursite.com', 'website.com'
        ]):
            filtered_emails.append(email)
    
    print(f"  ✅ Final result: {len(filtered_emails)} valid emails")
    return filtered_emails

async def scrape_multiple_urls(urls: List[str]) -> dict:
    """
    Scrape emails from multiple URLs concurrently
    Returns dict mapping URL to list of emails
    """
    results = {}
    
    # Process URLs in batches to avoid overwhelming servers
    batch_size = 3
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        
        # Create tasks for concurrent scraping
        tasks = [scrape_emails_hybrid(url) for url in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store results
        for url, emails in zip(batch, batch_results):
            if isinstance(emails, Exception):
                results[url] = []
            else:
                results[url] = emails
        
        # Small delay between batches
        if i + batch_size < len(urls):
            await asyncio.sleep(1)
    
    return results

def format_emails_for_csv(emails: List[str]) -> str:
    """Format email list for CSV storage"""
    if not emails:
        return ""
    return "|".join(emails)

def parse_emails_from_csv(email_string: str) -> List[str]:
    """Parse emails from CSV format back to list"""
    if not email_string or email_string.strip() == "":
        return []
    return [email.strip() for email in email_string.split("|") if email.strip()]

# Test function
async def test_scraper():
    """Test the email scraper with sample URLs"""
    test_urls = [
        "https://example.com",
        "https://github.com",
        "http://theowl.nyc/"
    ]
    
    print("🧪 Testing email scraper...")
    results = await scrape_multiple_urls(test_urls)
    
    for url, emails in results.items():
        print(f"\n🌐 {url}")
        if emails:
            for email in emails:
                print(f"  📧 {email}")
        else:
            print("  ❌ No emails found")

if __name__ == "__main__":
    asyncio.run(test_scraper())
