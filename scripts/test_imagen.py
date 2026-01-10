import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Using the stable 4.0 model if available
URL = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}"

def test_imagen():
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    prompt = "A cute cartoon dog holding a sign that says 'Hello World'"
    
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1
        }
    }

    headers = {"Content-Type": "application/json"}

    print(f"Testing Imagen API with prompt: '{prompt}'...")
    
    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for image content
        if 'predictions' in data and len(data['predictions']) > 0:
            b64_image = data['predictions'][0]['bytesBase64Encoded']
            
            with open("test_imagen_output.png", "wb") as f:
                f.write(base64.b64decode(b64_image))
            print("Success! Image saved to test_imagen_output.png")
        else:
            print("No predictions found in response.")
            print(data)

    except Exception as e:
        print(f"Error calling Imagen API: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

if __name__ == "__main__":
    test_imagen()
