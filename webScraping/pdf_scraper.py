import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import os
import re

#CODE best works in Local Computer Env as it downloads PDFs to local downloads dir
# Output folder
DOWNLOAD_DIR = "downloaded_pdfs"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "", text).strip().replace(" ", "_")[:150]

def get_pdf_links_with_titles(base_url):
    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find("body")
        if not body:
            print("[WARNING] No <body> tag found.")
            return []

        pdf_links = []
        current_h3 = "General"

        for elem in body.descendants:
            if elem.name == "h3":
                current_h3 = elem.get_text(strip=True)

            if elem.name == "a" and elem.has_attr("href") and elem["href"].lower().endswith(".pdf"):
                pdf_url = urljoin(base_url, elem["href"])
                if not is_valid_url(pdf_url):
                    continue

                link_text = elem.get_text(strip=True) or "untitled"
                prefix = sanitize_filename(current_h3)
                title = sanitize_filename(link_text)
                filename = f"{prefix} - {title}.pdf"

                pdf_links.append((pdf_url, filename))

        return pdf_links

    except Exception as e:
        print(f"[ERROR] Failed to extract PDF links from {base_url}: {e}")
        return []

def download_pdfs(pdf_links):
    for url, filename in tqdm(pdf_links, desc="📥 Downloading PDFs"):
        path = os.path.join(DOWNLOAD_DIR, filename)
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            with open(path, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f"[ERROR] Failed to download {url}: {e}")

if __name__ == "__main__":
    BASE_URL = "https://www.humboldt.edu/research/board/meetings-minutes-agendas?page=4"
    print(f"🔍 Searching for PDFs at: {BASE_URL}")

    pdf_links = get_pdf_links_with_titles(BASE_URL)
    print(f"🔗 Found {len(pdf_links)} PDF links.")

    if pdf_links:
        download_pdfs(pdf_links)
        print(f"✅ Done. PDFs saved in '{DOWNLOAD_DIR}'")
    else:
        print("⚠️ No PDFs found.")
