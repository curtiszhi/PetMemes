import requests
import os

# Directory to save images
SAVE_DIR = "input_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# List of high-quality pet images from Unsplash (IDs)
IMAGE_URLS = [
    ("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=2043&auto=format&fit=crop", "cat_1.jpg"), # Cat
    ("https://images.unsplash.com/photo-1543466835-00a7907e9de1?q=80&w=1974&auto=format&fit=crop", "dog_1.jpg"), # Dog
    ("https://images.unsplash.com/photo-1533738363-b7f9aef128ce?q=80&w=1935&auto=format&fit=crop", "cat_2.jpg"), # Funny Cat
    ("https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?q=80&w=2069&auto=format&fit=crop", "dog_2.jpg"), # Dog 2
    ("https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?q=80&w=2000&auto=format&fit=crop", "pug_1.jpg"), # Pug
]

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
    print("Fetching pet images...")
    for url, filename in IMAGE_URLS:
        download_image(url, filename)
    print("Done! Images saved to 'input_images/'")

if __name__ == "__main__":
    main()
