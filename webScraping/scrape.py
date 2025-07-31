import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import time

def is_valid_url(url):
    #Takes URL if its valid or not
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_body_links(base_url):
    #Goes into Body tag of HTML and replaces inside content of the Body Tag
    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find("body")
        if not body:
            print("[WARNING] No <body> tag found.")
            return set()

        links = set()
        for a_tag in body.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(base_url, href)
            if is_valid_url(full_url) and urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.add(full_url)
        return links
    except Exception as e:
        print(f"[ERROR] Failed to get body links from {base_url}: {e}")
        return set()

def get_visible_text(url):
    #Goes check the URL and scrapes the name inside URL
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(f"[ERROR] Failed to get text from {url}: {e}")
        return ""

def scrape_website(base_url):
    #Creates the Web Applcation
    visited = set()
    all_text = ""

    print(f"Scanning {base_url} for links in <body>...")
    links = get_body_links(base_url)
    links.add(base_url)

    print("Found {len(links)} pages to visit.")
    for link in tqdm(links):
        if link not in visited:
            visited.add(link)
            page_text = get_visible_text(link)
            if page_text:
                all_text += f"\n\n---\n {link}\n{page_text}"
            time.sleep(1)
    return all_text

if __name__ == "__main__":
    BASE_URL = "https://www.humboldt.edu/research/z-forms-library"
    scraped_text = scrape_website(BASE_URL)

    with open("humboldt_body_links_text.txt", "w", encoding="utf-8") as f:
        f.write(scraped_text)

    print("'humboldt_body_links_text.txt'")


