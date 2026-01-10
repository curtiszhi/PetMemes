import requests
import os
import json
import base64
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
INPUT_DIR = "input_images_v2"
OUTPUT_DIR = "output_memes_v2"
PROMPTS_FILE = "prompts_v2.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_caption(image_path, persona):
    base64_image = encode_image(image_path)
    
    prompt_text = (
        f"Look at this image. Write a short, funny meme caption in the style of: '{persona}'. "
        "The caption should be punchy, relatable, and suitable for a large thumbnail. "
        "Return ONLY the caption text (UPPERCASE is better for memes), nothing else. No quotes."
    )

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                }
            ]
        }]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        caption = data['candidates'][0]['content']['parts'][0]['text'].strip()
        return caption
    except Exception as e:
        print(f"Error generating caption for {persona}: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        return None

def add_caption_to_image(image_path, caption, output_filename):
    try:
        img = Image.open(image_path)
        
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # V2: Much larger font (scaling based on image width)
        # Target font size ~1/10th of image width
        font_size = int(width / 15) 
        if font_size < 40: font_size = 40 # min size
        
        try:
            # Try to load a bold font if possible
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=font_size, index=1) # index 1 often bold
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", size=font_size) 
            except:
                font = ImageFont.load_default() # Fallback

        # V2: ALL CAPS usually looks better for memes
        text_content = caption.upper()

        # Wrap text logic with wider lines
        words = text_content.split()
        lines = []
        current_line = []
        
        # Approximate char limit per line based on font size/width
        # A rough heuristic: width / (font_size * 0.6) chars
        chars_per_line = int(width / (font_size * 0.5))
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > chars_per_line:
                 lines.append(" ".join(current_line))
                 current_line = []
        if current_line:
            lines.append(" ".join(current_line))
            
        text = "\n".join(lines)
        
        # Position - Bottom Center
        # Calculate text block height
        # getbbox or multiline_textbbox is better but requires newer Pillow
        # Approximation:
        line_height = font_size * 1.2
        text_block_height = len(lines) * line_height
        
        x = width / 2
        y = height - text_block_height - (height * 0.05) # 5% padding from bottom
        
        # V2: Thicker stroke
        stroke_width = int(font_size / 10)
        if stroke_width < 1: stroke_width = 1

        draw.multiline_text(
            (x, y), 
            text, 
            font=font, 
            fill="white", 
            stroke_width=stroke_width, 
            stroke_fill="black", 
            anchor="mm", 
            align="center"
        )
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        img.save(output_path)
        print(f"Saved V2 meme: {output_filename}")
        
    except Exception as e:
        print(f"Error creating meme image: {e}")

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"No input images found in {INPUT_DIR}")
        return

    if not os.path.exists(PROMPTS_FILE):
        print(f"No prompts file found at {PROMPTS_FILE}")
        return

    with open(PROMPTS_FILE, "r") as f:
        prompts = json.load(f)

    images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Sort to ensure consistent order/duplication handling if any
    images.sort()
    
    if not images:
        print("No images to process.")
        return

    print(f"Found {len(images)} images and {len(prompts)} prompts. Generating V2 memes...")
    
    for i in range(min(5, len(prompts), len(images))):
        image_name = images[i]
        prompt = prompts[i]
        
        image_path = os.path.join(INPUT_DIR, image_name)
        print(f"Processing {image_name} with style: {prompt}")
        
        caption = generate_caption(image_path, prompt)
        
        if caption:
            print(f"Generated Caption: {caption}")
            output_filename = f"meme_v2_{i+1}_{image_name}"
            add_caption_to_image(image_path, caption, output_filename)

    print("Meme generation V2 complete!")

if __name__ == "__main__":
    main()
