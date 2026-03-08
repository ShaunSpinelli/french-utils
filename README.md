# Anki Card Generator

A Python-based workflow for generating high-quality Anki flashcards with images and audio.

## Features

- 🔊 **ElevenLabs Audio**: Generates natural-sounding French audio using the ElevenLabs API.
- 🖼️ **Image Hashing**: Uses content-based hashing (MD5) to force Anki to update cards when you replace an image with a new one of the same name.
- 🛠️ **Custom Image Workflow**: A multi-step process for manually selecting and downloading high-quality images.
- 🧹 **Automatic Cleanup**: Automatically removes old hashed versions of images when new ones are created.

## Prerequisites

- Python 3.7+
- ElevenLabs API key ([Get one here](https://elevenlabs.io/))
- `genanki`, `requests`, `python-dotenv` (see `requirements.txt`)

## Installation

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file:
   - Create a `.env` file in the root directory.
   - Add your API key: `ELEVEN_API_KEY=your_key_here`.

## Workflow: How to Generate Cards

The system uses a 3-step process to ensure your cards have the perfect images:

### 1. Identify Missing Images
Run `gen_cards.py`. It reads your CSV (e.g., `french_nouns_top10.csv`), generates audio, and checks for existing images in `data/media/`.

```bash
python gen_cards.py
```

If an image is missing, the script will:
- Print a warning.
- Add the entry to `image_links.txt`.
- Add a card to the deck with a placeholder image.

### 2. Add Image URLs
Open `image_links.txt`. You will see lines like:
`data/media/un_avion.jpg, plane [ADD URL HERE]`

Replace `[ADD URL HERE]` with a direct link to an image (e.g., from Unsplash, Pixabay, or Pexels).

### 3. Download and Hash
Run `update_verbs_card.py` to download the images:

```bash
python update_verbs_card.py
```

Finally, run `gen_cards.py` again. It will:
- See the new images.
- Generate a unique hash for each image (e.g., `un_avion_a1b2c3d4.jpg`).
- Create the final Anki package (`.apkg`) pointing to these unique files.

### 4. Import to Anki
Import the generated `.apkg` file located in the `data/` or `french_grammer/` folders into Anki.

## Configuration

- **`gen_cards.py`**: Main script for nouns/images.
- **`french_grammar.py`**: Script for grammar cloze cards.
- **`french_vocab.py`**: Script for vocabulary cards.
- **`CSV_FILE`**: Change this in each script to point to your data source.

## Technical Notes

- **Content Hashing**: Anki often caches media. By appending a hash of the file content to the filename (e.g., `image_abc123.jpg`), we ensure that when you change the image content, Anki recognizes it as a new file and updates the card immediately.
- **Media Storage**: Source images are stored as `name.jpg`, while the versions used in Anki are stored as `name_hash.jpg`.
- **Stable IDs & Study Progress**: 
    - Each script uses a permanent **Model ID** and **Deck ID**. 
    - Each card is assigned a stable **GUID** (globally unique identifier) based on the French word/sentence.
    - **Why this matters**: This allows you to update your CSV files periodically (adding new words or changing images) without losing your study progress. When you import the updated `.apkg`, Anki matches the GUIDs, updates the fields (like new images), and **preserves your review history, intervals, and due dates**.

## License

MIT License
