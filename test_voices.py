import os
import requests
import tempfile
import time
import pygame
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "YOUR_ELEVEN_API_KEY")

# Voice IDs to test
VOICE_IDS = [
    # "dYjOkSQBPiH2igolJfeH",
"SAz9YHcvj6GT2YYXdXww"
    # Add more voice IDs here to test
]

# Test texts (including French)
TEST_TEXTS = ["Je prends le bus le matin", "Maintenant Monsieur Scott, je vais prendre votre température.", "ecureuil"]

def play_audio(audio_content):
    """Play audio content using pygame"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
        temp_audio.write(audio_content)
        temp_path = temp_audio.name
    
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_voice(voice_id):
    """Test if a voice ID is accessible and play the audio"""
    for test_text in TEST_TEXTS:
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
        headers = {
            'accept': 'audio/mpeg',
            'xi-api-key': ELEVEN_API_KEY,
            'Content-Type': 'application/json',
        }
        data = {
            'text': test_text,
            'model_id': 'eleven_multilingual_v2',
            "voice_settings": {
                "stability": 0.85,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True
            },
            "voice_generation": {
                "speed": 0.5
            }
        }
        
        try:
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                print(f"   ✓ '{test_text}' - Success ({len(resp.content)} bytes). Playing...")
                play_audio(resp.content)
            else:
                error_info = resp.json() if 'application/json' in resp.headers.get('content-type', '') else resp.text
                print(f"   ✗ '{test_text}' - Failed: {error_info}")
                return False, error_info
        except Exception as e:
            return False, str(e)
    
    return True, "All tests passed"

def main():
    print(f"Testing {len(VOICE_IDS)} voice ID(s)...\n")
    print("="*60)
    
    working_voices = []
    failed_voices = []
    
    for voice_id in VOICE_IDS:
        print(f"\nTesting voice ID: {voice_id}")
        success, message = test_voice(voice_id)
        
        if success:
            print(f"✅ WORKING")
            working_voices.append(voice_id)
        else:
            print(f"❌ FAILED")
            print(f"   Error: {message}")
            failed_voices.append((voice_id, message))
    
    print("\n" + "="*60)
    print("\n📊 SUMMARY:")
    print(f"Total tested: {len(VOICE_IDS)}")
    print(f"Working: {len(working_voices)}")
    print(f"Failed: {len(failed_voices)}")
    
    if working_voices:
        print("\n✅ WORKING VOICE IDs:")
        for voice_id in working_voices:
            print(f"   - {voice_id}")
    
    if failed_voices:
        print("\n❌ FAILED VOICE IDs:")
        for voice_id, error in failed_voices:
            print(f"   - {voice_id}")

if __name__ == "__main__":
    main()

