"""
French Vocabulary Card Generator

This script generates Anki cards for French vocabulary practice.
Audio is generated using ElevenLabs and plays on the answer side.
The audio includes the target word followed by the example sentence.

CSV FORMAT REQUIRED:
The CSV file must have the following columns:
- french_word: The target word in French
- eng_word: The English definition
- french_sentce: An example sentence in French
- english_sentece: The English translation of the example sentence

"""

import csv
import requests
import genanki
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------
# CONFIGURATION
# -----------------------
CSV_FILE = "french_vocab.csv"

# ElevenLabs API
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
# Using the same voice ID as the grammar script
# ELEVEN_VOICE_ID = "rgFgMEXfdGwXCYio7I0J" py   
ELEVEN_VOICE_ID = "EXAVITQu4vr4xnSDxMaL" # Bella (Standard Voice)

# Output directories
OUTPUT_DIR = "french_vocab_deck"
MEDIA_DIR = os.path.join(OUTPUT_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# -----------------------
# HELPER FUNCTIONS
# -----------------------

def generate_audio_eleven(text, save_path):
    """
    Generates audio using ElevenLabs API.
    Returns the save_path if successful, None otherwise.
    """
    if not ELEVEN_API_KEY:
        print("Error: ELEVEN_API_KEY not found in environment variables.")
        return None

    url = f'https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}'
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': ELEVEN_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'text': text,
        'model_id': 'eleven_multilingual_v2',
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(resp.content)
            return save_path
        else:
            print(f"Error generating audio for '{text}': {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"Exception during audio generation: {e}")
        return None

def sanitize_filename(text):
    """
    Creates a safe filename from text.
    """
    return "".join([c if c.isalnum() else "_" for c in text])[:50].lower()

# -----------------------
# CREATE ANKI DECK
# -----------------------

# Model for Vocabulary Cards (Basic Front/Back)
MODEL_ID = 1892345678
DECK_ID = 2109876543

model = genanki.Model(
    MODEL_ID,
    'French Vocabulary Model',
    fields=[
        {'name': 'FrenchWord'},
        {'name': 'EnglishDefinition'},
        {'name': 'FrenchSentence'},
        {'name': 'EnglishSentenceTranslation'},
        {'name': 'Audio'},
    ],
    templates=[
        {
            'name': 'Vocab Card',
            'qfmt': '''
                <div class="card-content">
                    <div class="target-word">{{FrenchWord}}</div>
                </div>
            ''',
            'afmt': '''
                <div class="card-content">
                    <div class="target-word">{{FrenchWord}}</div>
                </div>
                
                <hr id="answer">
                
                <div class="card-content">
                    <div class="definition">{{EnglishDefinition}}</div>
                    <br>
                    <div class="sentence-fr">{{FrenchSentence}}</div>
                    <br>
                    <div class="sentence-en">{{EnglishSentenceTranslation}}</div>
                    <br>
                    <div class="audio">{{Audio}}</div>
                </div>
            ''',
        }
    ],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: #2c3e50;
            background-color: white;
        }
        /* Dark Mode Support */
        .night_mode .card {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        
        .card-content {
            margin: 10px;
        }
        
        .target-word {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }
        .night_mode .target-word {
            color: #ecf0f1;
        }

        .definition {
            font-size: 22px;
            color: #2980b9;
        }
        .night_mode .definition {
            color: #5dade2;
        }

        .sentence-fr {
            font-size: 20px;
            color: #2c3e50;
            margin-top: 10px;
        }
        .night_mode .sentence-fr {
            color: #ecf0f1;
        }

        .sentence-en {
            font-size: 18px;
            color: #7f8c8d;
        }
        .night_mode .sentence-en {
            color: #bdc3c7;
        }
    '''
)

deck = genanki.Deck(
    DECK_ID,
    'French Vocabulary Deck'
)

media_files = []

# -----------------------
# PROCESS CSV
# -----------------------

if not os.path.exists(CSV_FILE):
    print(f"Error: {CSV_FILE} not found.")
else:
    print(f"Reading {CSV_FILE}...")
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        # Normalize headers by stripping whitespace
        fieldnames = [h.strip() for h in next(csv.reader(csvfile))]
        csvfile.seek(0) 
        
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        next(reader) # Skip header row
        
        for row in reader:
            # robustly get fields handling potential whitespace in headers
            french_word = row.get('french_word', '').strip()
            eng_word = row.get('eng_word', '').strip()
            french_sentce = row.get('french_sentce', '').strip()
            english_sentece = row.get('english_sentece', '').strip()

            if not french_word:
                continue

            print(f"Processing: {french_word}")

            # Audio Generation Logic
            # Content: "Word. Sentence."
            audio_text = f"{french_word}. {french_sentce}"
            filename_base = sanitize_filename(f"{french_word}_{french_sentce}"[:40])
            audio_filename = f"vocab_{filename_base}.mp3"
            audio_path = os.path.join(MEDIA_DIR, audio_filename)
            
            audio_tag = ""
            
            # Check if audio exists
            if os.path.exists(audio_path):
                print(f"  - Audio found locally: {audio_filename}")
                media_files.append(audio_path)
                audio_tag = f'[sound:{audio_filename}]'
            else:
                print(f"  - Generating audio...")
                if generate_audio_eleven(audio_text, audio_path):
                    media_files.append(audio_path)
                    audio_tag = f'[sound:{audio_filename}]'
                    print(f"  - Audio generated.")
                else:
                    print(f"  - Audio generation failed.")

            # Add Note with stable GUID
            note_id = genanki.guid_for(f"{french_word}_{french_sentce}")
            note = genanki.Note(
                model=model,
                fields=[
                    french_word,
                    eng_word,
                    french_sentce,
                    english_sentece,
                    audio_tag
                ],
                guid=note_id
            )
            deck.add_note(note)

    # -----------------------
    # PACKAGE AND SAVE
    # -----------------------
    package = genanki.Package(deck)
    package.media_files = media_files
    output_file = os.path.join(OUTPUT_DIR, 'french_vocab_deck.apkg')
    package.write_to_file(output_file)
    print(f"\nSuccess! Deck created at: {output_file}")
    print(f"Total cards: {len(deck.notes)}")
