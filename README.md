# Scalable Pet Meme Generator 🐶🐱

A fully automated pipeline that transforms ordinary pet photos into diverse, hilarious, human-like memes using Google's generative AI.

## Overview

This project uses a "Mass Production" approach to create unlimited meme variations from a single pet photo:
1.  **See**: Uses **Gemini Vision** to describe your pet (breed, markings, expression).
2.  **Imagine**: Applies a library of creative "Styles" (e.g., "Frantically Typing", "DJing", "Renaissance Painting") to the pet's description.
3.  **Generate**: Uses **Imagen** to create a text-free, visual transformation of your pet performing human activities.
4.  **Meme-ify**: Uses **Gemini** to write a funny caption and **Pillow** to render it dynamically onto the image.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install requests python-dotenv Pillow
    ```

2.  **Configure API Key**:
    - Create a `.env` file in the project root.
    - Add your Gemini API Key:
      ```env
      GEMINI_API_KEY=your_api_key_here
      ```

3.  **Add Input Images**:
    - Place your "normal" pet photos (jpg/png) in the `input_images/` directory.
    - The filenames (e.g., `cat_base.jpg`) determine the subject name.

## Running the Pipeline

To generate memes for all images in `input_images/` using the styles in `meme_styles.json`:

```bash
python3 scripts/3_run_pipeline.py
```

### Outputs
- The generated memes will appear in the `output_memes/` folder.
- Format: `[pet_name]_meme_style_[style_index].jpg`

## Key Scripts

- `scripts/1_fetch_images.py`: (Optional) Downloads sample pet images.
- `scripts/2_generate_styles.py`: Generates the `meme_styles.json` library of prompts (ensuring human-like activities).
- `scripts/3_run_pipeline.py`: The main script. Handles vision interpretation, image generation, rate limiting, captioning, and rendering.

## Note on Rate Limits
The pipeline includes a **30-second delay** between image generations to adhere to API rate limits (Avoids 429 errors). Please be patient when running the script!
