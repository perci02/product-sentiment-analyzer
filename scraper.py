import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def _get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


# ────────────────────────────────────────
# Flipkart Scraper
# ────────────────────────────────────────

def scrape_flipkart(product_name, max_reviews=30):
    """Scrape product reviews from Flipkart search results."""
    reviews = []
    try:
        # Step 1: Search for the product
        search_url = f"https://www.flipkart.com/search?q={quote_plus(product_name)}"
        resp = requests.get(search_url, headers=_get_headers(), timeout=10)
        if resp.status_code != 200:
            return reviews

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find product links from search results
        product_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/p/" in href and href not in product_links:
                product_links.append(href)
                if len(product_links) >= 3:
                    break

        if not product_links:
            return reviews

        # Step 2: Visit product pages and extract reviews
        for link in product_links:
            if len(reviews) >= max_reviews:
                break

            product_url = "https://www.flipkart.com" + link if link.startswith("/") else link
            time.sleep(1)  # polite delay

            try:
                resp = requests.get(product_url, headers=_get_headers(), timeout=10)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                # Flipkart review containers — try multiple known selectors
                review_divs = soup.find_all("div", class_="ZmyHeo")
                if not review_divs:
                    review_divs = soup.find_all("div", class_="t-ZTKy")
                if not review_divs:
                    # Fallback: look for review text in common patterns
                    review_divs = soup.find_all("div", {"class": lambda c: c and "review" in c.lower()})

                for div in review_divs:
                    text = div.get_text(strip=True)
                    if text and len(text) > 20:
                        reviews.append(text)
                        if len(reviews) >= max_reviews:
                            break

            except (requests.RequestException, Exception):
                continue

    except (requests.RequestException, Exception):
        pass

    return reviews


# ────────────────────────────────────────
# Amazon Scraper
# ────────────────────────────────────────

def scrape_amazon(product_name, max_reviews=30):
    """Scrape product reviews from Amazon.in search results."""
    reviews = []
    try:
        # Step 1: Search for the product
        search_url = f"https://www.amazon.in/s?k={quote_plus(product_name)}"
        resp = requests.get(search_url, headers=_get_headers(), timeout=10)
        if resp.status_code != 200:
            return reviews

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find ASINs from search results
        asins = []
        for div in soup.find_all("div", attrs={"data-asin": True}):
            asin = div.get("data-asin", "").strip()
            if asin and len(asin) == 10 and asin not in asins:
                asins.append(asin)
                if len(asins) >= 3:
                    break

        if not asins:
            return reviews

        # Step 2: Visit review pages for each product
        for asin in asins:
            if len(reviews) >= max_reviews:
                break

            review_url = f"https://www.amazon.in/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
            time.sleep(1)  # polite delay

            try:
                resp = requests.get(review_url, headers=_get_headers(), timeout=10)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                # Amazon review text spans
                review_spans = soup.find_all("span", attrs={"data-hook": "review-body"})

                for span in review_spans:
                    inner = span.find("span")
                    text = (inner or span).get_text(strip=True)
                    if text and len(text) > 20:
                        reviews.append(text)
                        if len(reviews) >= max_reviews:
                            break

            except (requests.RequestException, Exception):
                continue

    except (requests.RequestException, Exception):
        pass

    return reviews


# ────────────────────────────────────────
# Combined Scraper
# ────────────────────────────────────────

def scrape_reviews(product_name):
    """
    Scrape reviews from Flipkart and Amazon.
    Returns a list of review text strings.
    """
    all_reviews = []

    # Try Flipkart first (more reliable for scraping)
    flipkart_reviews = scrape_flipkart(product_name)
    all_reviews.extend(flipkart_reviews)

    # Then Amazon
    amazon_reviews = scrape_amazon(product_name)
    all_reviews.extend(amazon_reviews)

    # Deduplicate (exact matches)
    seen = set()
    unique = []
    for r in all_reviews:
        if r not in seen:
            seen.add(r)
            unique.append(r)

    return unique
