# Implementation Plan - Pet Meme Generator V2 (Scalable Library)

The goal is to build a system that can "mass produce" memes by applying a set of diverse, creative **Prompt Styles** to *any* real pet image.

## User Review Required
> [!IMPORTANT]
> **Workflow Shift**: Instead of generating a prompt *for* an image, we will generate a **Library of Meme Styles** (e.g., "Pixel Art", "Corporate Headshot", "Superhero") and apply them to the pet images.
> **Diversity**: The library will include realistic, semi-realistic, cartoon, and artistic styles.

## Proposed Architecture

### 1. Image Acquisition (`scripts/1_fetch_images_v2.py`)
- (Done) We have the set of base pet images.

### 2. Style Library Generation (`scripts/2_generate_styles_v2.py`)
- **Goal**: Create 10 diverse "Prompt Templates".
- **Format**: Strings with a placeholder, e.g., "A {style} image of {pet_description} [doing action]..."
- **Styles**: Realistic, 3D, Sketch, Retro, etc.
- **Output**: `meme_styles_v2.json`.

### 3. Mass Production Pipeline (`scripts/3_run_pipeline_v2.py`)
- **Process per Image**:
    1.  **Analyze**: Use Gemini Vision to get a concise `{pet_description}` (e.g., "a fluffy golden retriever with happy eyes").
    2.  **Iterate Styles**: Loop through the 10 styles.
    3.  **Combine**: Form the full prompt: Style Template + Pet Description.
    4.  **Generate**: Call `imagen-4.0` to create the new image.
    5.  **Meme-ify**:
        - Generate funny caption (Gemini).
        - Render large text (Pillow).
- **Output**: `mass_produced_memes/`

## Verification Plan
- **Manual**: Check that the output folder contains multiple variations (styles) of the same original pets.
