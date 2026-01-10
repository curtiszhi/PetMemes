import requests
import os
import json
import base64
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
INPUT_DIR = "generated_images_v2"
OUTPUT_DIR = "output_memes_v2"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_caption(image_path):
    base64_image = encode_image(image_path)
    
    prompt_text = (
        "Look at this image. Write a short, funny meme caption for it. "
        "The caption should be punchy, relatable, and suitable for a large thumbnail. "
        "Return ONLY the caption text (UPPERCASE is usually better), nothing else. No quotes."
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
        print(f"Error generating caption: {e}")
        return None

def add_caption_to_image(image_path, caption, output_filename):
    try:
        img = Image.open(image_path)
        
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # V2 Style: Large font
        font_size = int(width / 15) 
        if font_size < 40: font_size = 40 
        
        try:
            # Try to load a bold font
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=font_size, index=1)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", size=font_size) 
            except:
                font = ImageFont.load_default() 

        text_content = caption.upper()

        # Wrap text
        chars_per_line = int(width / (font_size * 0.5))
        
        words = text_content.split()
        lines = []
        current_line = []
        
        for word in words:
             current_line.append(word)
             if len(" ".join(current_line)) > chars_per_line:
                 lines.append(" ".join(current_line))
                 current_line = []
        if current_line:
            lines.append(" ".join(current_line))
            
        text = "\n".join(lines)
        
        # Position - Bottom Center w/ Padding
        line_height = font_size * 1.2
        text_block_height = len(lines) * line_height
        
        x = width / 2
        y = height - text_block_height - (height * 0.05) 
        
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
        print(f"Saved meme: {output_filename}")
        
    except Exception as e:
        print(f"Error creating meme image for {output_filename}: {e}")

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"No input images found in {INPUT_DIR}")
        return

    images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    images.sort()
    
    if not images:
        print("No images to process.")
        return

    print(f"Found {len(images)} generated images. Assembling memes...")
    
    for image_name in images:
        image_path = os.path.join(INPUT_DIR, image_name)
        print(f"Processing {image_name}...")
        
        caption = generate_caption(image_path)
        
        if caption:
            print(f"Generated Caption: {caption}")
            output_filename = f"meme_{image_name}"
            add_caption_to_image(image_path, caption, output_filename)

    print("Meme assembly complete!")

if __name__ == "__main__":
    main()
