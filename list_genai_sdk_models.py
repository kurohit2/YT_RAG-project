import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_sdk_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("Models available via google-genai SDK:")
    for m in client.models.list():
        print(f"Name: {m.name}, Display: {m.display_name}")

if __name__ == "__main__":
    list_sdk_models()
