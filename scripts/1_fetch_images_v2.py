import requests
import os
import re

# Directory to save images
SAVE_DIR = "input_images_v2"
os.makedirs(SAVE_DIR, exist_ok=True)

# Unsplash Page URLs (Source)
PAGE_URLS = [
    ("https://unsplash.com/photos/xW1oQ53w3iY", "dog_reading.jpg"),
    ("https://unsplash.com/photos/vH_L6A-o5y8", "cat_sunglasses.jpg"),
    ("https://unsplash.com/photos/C0YFv-xM8pM", "cat_glasses_head.jpg"),
    ("https://unsplash.com/photos/bY4-x8J5z8c", "cat_glasses_look.jpg"),
    ("https://unsplash.com/photos/N04FIfHhv_k", "dog_sunglasses_2.jpg")
]

def get_image_url_from_page(page_url):
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        html = response.text
        
        # Simple regex to find og:image
        # <meta property="og:image" content="https://images.unsplash.com/photo-...?..." />
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if match:
            return match.group(1)
        else:
            print(f"Could not find og:image in {page_url}")
            return None
    except Exception as e:
        print(f"Error fetching page {page_url}: {e}")
        return None

def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        filepath = os.path.join(SAVE_DIR, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

def main():
    print("Fetching human-like pet images for V2 (Scraping)...")
    for page_url, filename in PAGE_URLS:
        print(f"Processing {filename}...")
        image_url = get_image_url_from_page(page_url)
        if image_url:
            download_image(image_url, filename)
        else:
            print(f"Skipping {filename} - no URL found.")
    print(f"Done! Images saved to '{SAVE_DIR}'")

if __name__ == "__main__":
    main()
