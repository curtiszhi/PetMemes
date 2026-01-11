import requests
import os
import json
import base64
import time
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# ... imports remain ...
import requests
import os
import json
import base64
import time
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
IMAGEN_URL = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

INPUT_DIR = "input_images"
OUTPUT_DIR = "output_memes"
# STYLES_FILE not needed anymore
# STYLES_FILE = "meme_styles.json" 

ACTIVITIES = [
    ("typing", "typing frantically on a mechanical keyboard in a chaotic office"),
    ("spa", "reading a book while relaxing in a lush spa with cucumber slices on eyes and a towel on head")
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Rewritten to generate the FULL prompt based on image + activity
def generate_transformation_prompt(image_path, activity_description):
    base64_image = encode_image(image_path)
    
    # Prompt engineering for the Vision model to act as a Prompt Engineer
    prompt_request = (
        f"Act as an expert prompt engineer. Look at this pet in the image. "
        f"I want to generate a new high-quality, photorealistic image of THIS SPECIFIC PET {activity_description}. "
        f"Write a detailed image generation prompt that describes the pet's physical features (breed, exact color, patterns, eye color) "
        f"based on the image, and places them in the scene described. "
        f"The output should be ONLY the prompt string, nothing else."
    )
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_request},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
            ]
        }]
    }
    
    try:
        response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Error generating prompt: {e}")
        return None

def generate_image_from_prompt(prompt, output_filename):
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    if os.path.exists(output_path):
        return output_path

    print(f"Generating image for prompt: {prompt[:50]}...")
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }
    
    try:
        response = requests.post(IMAGEN_URL, headers={"Content-Type": "application/json"}, json=payload)
        # Handle non-200
        if response.status_code != 200:
             print(f"Error {response.status_code}: {response.text}")
             return None
             
        data = response.json()
        
        if 'predictions' in data:
            b64_img = data['predictions'][0]['bytesBase64Encoded']
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64_img))
            print(f"Image saved: {output_filename}")
            print("Sleeping for 30s to respect rate limits...")
            time.sleep(30)
            return output_path
    except Exception as e:
        print(f"Error generating image: {e}")
    return None

def generate_caption(image_path):
    base64_image = encode_image(image_path)
    prompt_text = "Write a VERY SHORT, punchy, funny meme caption for this image. Max 8 words. UPPERCASE text only. No quotes."
    
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

def render_meme(image_path, caption, output_filename):
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Start with large font
        font_size = int(width / 12) 
        min_font_size = 20
        margin = width * 0.05
        max_text_width = width - (2 * margin)

        # Iterative fitting
        while font_size >= min_font_size:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=font_size, index=1)
            except:
                font = ImageFont.load_default()

            lines = []
            words = caption.split()
            current_line = []
            
            valid_size = True
            for word in words:
                test_line = " ".join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                w = bbox[2] - bbox[0]
                
                if w <= max_text_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        bbox = draw.textbbox((0, 0), word, font=font)
                        if (bbox[2] - bbox[0]) > max_text_width:
                             valid_size = False
                             break
                    else:
                        valid_size = False
                        break
            
            if valid_size and current_line:
                lines.append(" ".join(current_line))
            
            if valid_size:
                 break
            
            font_size -= 2
        
        text = "\n".join(lines)
        
        # Calculate Height
        line_height = font_size * 1.2
        text_height = len(lines) * line_height
        bottom_margin = height * 0.05
        y_top = height - text_height - bottom_margin
        if y_top < 0: y_top = 0
        
        stroke_width = max(1, int(font_size/12))
        
        draw.multiline_text(
            (width/2, y_top),
            text, 
            font=font, 
            fill="white", 
            stroke_width=stroke_width, 
            stroke_fill="black", 
            anchor="ma", 
            align="center"
        )
        
        meme_path = os.path.join(OUTPUT_DIR, output_filename)
        img.save(meme_path)
        print(f"Created meme: {meme_path}")
        return meme_path
    except Exception as e:
        print(f"Error rendering meme: {e}")
        return None

def main():
    if not os.path.exists(INPUT_DIR):
        print("Missing input directory.")
        return
    
    input_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    input_files.sort()
    
    if not input_files:
        print("No input images found.")
        return

    print("Running New 'Vision-Imagination' Pipeline (Typing & Spa)...")

    for filename in input_files:
        print(f"\n--- Processing {filename} ---")
        pet_name = filename.split('_')[0]
        
        # Loop over specific activities
        for activity_name, activity_desc in ACTIVITIES:
            print(f"Activity: {activity_name}")
            
            # 1. Vision -> Prompt
            print("Creating prompt from image...")
            imagen_prompt = generate_transformation_prompt(os.path.join(INPUT_DIR, filename), activity_desc)
            if not imagen_prompt:
                continue
            
            # 2. Prompt -> Image
            temp_raw_filename = f"temp_{pet_name}_{activity_name}.png"
            final_meme_filename = f"{pet_name}_{activity_name}_meme.jpg"
            
            gen_path = generate_image_from_prompt(imagen_prompt, temp_raw_filename)
            
            # 3. Image -> Caption -> Meme
            if gen_path:
                caption = generate_caption(gen_path)
                if caption:
                    print(f"Caption: {caption}")
                    render_meme(gen_path, caption, final_meme_filename)
                
                # Cleanup
                try:
                    os.remove(gen_path)
                    print("Deleted temp file.")
                except:
                    pass

if __name__ == "__main__":
    main()
