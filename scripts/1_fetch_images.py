import requests
import os

# Directory to save images
SAVE_DIR = "input_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# List of high-quality "Normal" pet images (Base for transformation)
IMAGE_URLS = [
    ("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=2043&auto=format&fit=crop", "cat_base.jpg"), 
    ("https://images.unsplash.com/photo-1543466835-00a7907e9de1?q=80&w=1974&auto=format&fit=crop", "dog_base.jpg"), 
    ("https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?q=80&w=2000&auto=format&fit=crop", "pug_base.jpg"), 
    ("https://images.unsplash.com/photo-1425082661705-1834bfd09dca?q=80&w=2076&auto=format&fit=crop", "hamster_base.jpg"),
    ("https://images.unsplash.com/photo-1517849845537-4d257902454a?q=80&w=1935&auto=format&fit=crop", "dog_chow.jpg")
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
    print("Fetching normal pet images for V2...")
    for url, filename in IMAGE_URLS:
        download_image(url, filename)
    print(f"Done! Images saved to '{SAVE_DIR}'")

if __name__ == "__main__":
    main()
