import re
import os

def remove_social_media_urls(text):
    social_media_domains = [
        'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
        'tiktok.com', 'youtube.com', 'pinterest.com', 'snapchat.com',
        'discord.com', 'reddit.com'
    ]
    pattern = r'https?://(?:www\.)?(?:' + '|'.join(re.escape(domain) for domain in social_media_domains) + r')[^\s]*'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

if __name__ == "__main__":
    input_path = "linkTextFile/external_links_from_research_pages.txt"
    output_path = "linkTextFile/cleaned_external_links_pages.txt"

    if not os.path.exists(input_path):
        print(f" Input file not found: {input_path}")
        exit(1)

    with open(input_path, "r", encoding="utf-8") as infile:
        raw_text = infile.read()

    cleaned = remove_social_media_urls(raw_text)

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(cleaned.strip())

    print(f" Cleaned file saved as: {output_path}")
