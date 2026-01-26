import requests
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

# Manual config for testing
load_dotenv()
BRIA_API_KEY = os.environ.get("BRIA_API_KEY")

def test_bria():
    print(f"Testing Bria with API Key: {BRIA_API_KEY[:4]}...")
    endpoint = "https://engine.bria.ai/v1/text-to-image/bria-2.3"
    headers = {"api_token": BRIA_API_KEY}
    
    prompt = """NotebookLM style information design, modular grid with rounded cards,
               soft pastel palette of muted teal and soft orange, 
               modern flat vector icons, professional information architecture,
               clean sans-serif typography, high-end UI design,
               educational illustration, minimalist data visualization,
               infographic about: The impact of AI on education and creativity."""
               
    payload = {
        "prompt": prompt,
        "negative_prompt": "text, words, blurry, photo",
        "aspect_ratio": "16:9",
        "sync_mode": True  # Easier for simple test
    }
    
    try:
        print("Sending request to Bria (sync mode)...")
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            image_url = data.get("result", {}).get("url")
            if image_url:
                print(f"Success! Image URL: {image_url}")
                img_res = requests.get(image_url)
                img = Image.open(BytesIO(img_res.content))
                img.save("test_bria_output.png")
                print("Image saved to test_bria_output.png")
            else:
                print(f"No image URL in response: {data}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_bria()
