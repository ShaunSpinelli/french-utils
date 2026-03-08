import os
import io
from google import genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google AI Studio API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def test_image_gen():
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY not found in .env file.")
        return

    print("🚀 Initializing Gemini Client...")
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    prompt = "A professional high-resolution studio photograph of a red apple, centered, isolated on a solid plain white background, sharp focus, soft cinematic lighting, 8k resolution, hyper-realistic."
    model_id = "gemini-2.5-flash-image"

    print(f"🎨 Attempting to generate image with model: {model_id}...")
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
        )
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_data = io.BytesIO(part.inline_data.data)
                    image = Image.open(image_data)
                    save_path = "test_generated_apple.jpg"
                    image.save(save_path)
                    print(f"✅ SUCCESS! Image saved to {save_path}")
                    return
        
        print("❌ No image data found in the response candidates.")
        print("Full Response Metadata:", response.usage_metadata)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_image_gen()
