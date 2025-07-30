import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import csv

# Target URL
BASE_URL = "https://www.humboldt.edu/research/board/meetings-minutes-agendas"

# Output folders
PDF_DIR = "humboldt_meeting_pdfs"
METADATA_CSV = "meeting_metadata.csv"

# Create output folder
os.makedirs(PDF_DIR, exist_ok=True)

def extract_pdf_links(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf'):
            full_url = urljoin(base_url, href)
            text = link.get_text(strip=True)
            pdf_links.append((full_url, text))

    return pdf_links

def infer_meeting_date(text_or_filename):
    # Try to extract a date pattern
    date_match = re.search(r'(\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b[\s\-\.]?\d{1,2},?\s?\d{4})', text_or_filename, re.IGNORECASE)
    if date_match:
        return date_match.group(1)

    date_match_alt = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text_or_filename)
    if date_match_alt:
        return date_match_alt.group(1)

    return "Unknown"

def download_pdfs_and_metadata(pdf_links):
    metadata = []

    for url, label in pdf_links:
        filename = os.path.basename(url).split("?")[0]
        save_path = os.path.join(PDF_DIR, filename)

        try:
            print(f"Downloading: {url}")
            response = requests.get(url)
            with open(save_path, 'wb') as f:
                f.write(response.content)

            date = infer_meeting_date(label + " " + filename)
            metadata.append({
                "file_name": filename,
                "url": url,
                "meeting_title": label,
                "meeting_date": date
            })

        except Exception as e:
            print(f"Failed to download {url}: {e}")

    return metadata

def save_metadata_to_csv(metadata, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "url", "meeting_title", "meeting_date"])
        writer.writeheader()
        for row in metadata:
            writer.writerow(row)

def main():
    pdf_links = extract_pdf_links(BASE_URL)
    metadata = download_pdfs_and_metadata(pdf_links)
    save_metadata_to_csv(metadata, METADATA_CSV)
    print(f"Downloaded {len(metadata)} PDFs and saved metadata to {METADATA_CSV}")

if __name__ == "__main__":
    main()
