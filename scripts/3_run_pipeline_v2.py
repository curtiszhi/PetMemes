import requests
import os
import json
import base64
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
IMAGEN_URL = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

INPUT_DIR = "input_images_v2"
OUTPUT_DIR = "mass_produced_memes"
STYLES_FILE = "meme_styles_v2.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_pet_description(image_path):
    base64_image = encode_image(image_path)
    prompt_text = "Describe this pet in detail (breed, color, markings, expression) in one sentence."
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
            ]
        }]
    }
    
    try:
        response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Error getting description: {e}")
        return None

def generate_image_from_prompt(prompt, filename_base):
    print(f"Generating image for prompt: {prompt[:50]}...")
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }
    
    try:
        response = requests.post(IMAGEN_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if 'predictions' in data:
            b64_img = data['predictions'][0]['bytesBase64Encoded']
            output_filename = f"gen_{filename_base}.png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64_img))
            return output_path
    except Exception as e:
        print(f"Error generating image: {e}")
    return None

def generate_caption(image_path):
    base64_image = encode_image(image_path)
    prompt_text = "Write a punchy, funny meme caption for this image. UPPERCASE text only. No quotes."
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": "image/png", "data": base64_image}}
            ]
        }]
    }
    
    try:
        response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        return None

def render_meme(image_path, caption):
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        font_size = max(40, int(width / 15))
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=font_size, index=1)
        except:
             font = ImageFont.load_default()

        # Wrap text
        chars = int(width / (font_size * 0.5))
        lines = []
        for line in caption.split('\n'):
             current = []
             for word in line.split():
                 current.append(word)
                 if len(" ".join(current)) > chars:
                     lines.append(" ".join(current))
                     current = []
             if current: lines.append(" ".join(current))
        
        text = "\n".join(lines)
        
        # Draw text at bottom
        y = height - (len(lines) * font_size * 1.2) - (height * 0.05)
        
        draw.multiline_text((width/2, y), text, font=font, fill="white", stroke_width=int(font_size/10), stroke_fill="black", anchor="mm", align="center")
        
        # Save over original generated file or new one? Let's overwrite for simplicity in this flow or append _meme
        meme_path = image_path.replace(".png", "_meme.jpg")
        img.save(meme_path)
        print(f"Created meme: {meme_path}")
        return meme_path
    except Exception as e:
        print(f"Error rendering meme: {e}")
        return None

def main():
    if not os.path.exists(INPUT_DIR) or not os.path.exists(STYLES_FILE):
        print("Missing inputs.")
        return

    with open(STYLES_FILE, "r") as f:
        styles = json.load(f)
    
    # Process just 2 images with 2 styles for demo speed/quota safety
    # In production, loop all
    input_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('base.jpg')][:2] 
    
    for filename in input_files:
        print(f"--- Processing {filename} ---")
        desc = get_pet_description(os.path.join(INPUT_DIR, filename))
        if not desc: continue
        print(f"Description: {desc}")
        
        # Use first 3 styles
        for i, style in enumerate(styles[:3]):
            final_prompt = style.format(pet_description=desc)
            gen_path = generate_image_from_prompt(final_prompt, f"{filename}_{i}")
            
            if gen_path:
                caption = generate_caption(gen_path)
                if caption:
                    render_meme(gen_path, caption)

if __name__ == "__main__":
    main()
