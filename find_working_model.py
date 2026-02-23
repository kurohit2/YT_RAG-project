import os
from google import genai
from dotenv import load_dotenv
import time

load_dotenv()

def find_working_model():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    models_to_test = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]
    
    print("Testing models for available quota...")
    for model_id in models_to_test:
        print(f"\nTesting {model_id}...")
        try:
            response = client.models.generate_content(
                model=model_id,
                contents="test"
            )
            print(f"SUCCESS: {model_id} works!")
            return model_id
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                print(f"FAILED: {model_id} - Quota Exceeded (429)")
            elif "404" in msg:
                print(f"FAILED: {model_id} - Not Found (404)")
            else:
                print(f"FAILED: {model_id} - {msg[:100]}")
        time.sleep(1) # Small delay between tests
    
    return None

if __name__ == "__main__":
    find_working_model()
