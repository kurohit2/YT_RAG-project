import os
import requests
from io import BytesIO
from PIL import Image
import json
import time
from config import Config

# Alternative: Using Pollinations.ai (Completely Free, No API Key)
class PollinationsGenerator:
    """
    Simpler alternative using Pollinations.ai - no API key required!
    """
    
    @staticmethod
    def generate_infographic(summary_text, style="modern", seed=42):
        """
        Generates infographic using Pollinations.ai free API.
        """
        style_modifiers = {
            "modern": "modern flat design infographic, vibrant colors, clean layout",
            "minimalist": "minimalist infographic, white background, simple icons",
            "colorful": "colorful vibrant infographic, gradient backgrounds",
            "professional": "professional business infographic, corporate style",
            "notebooklm": "NotebookLM style infographic, soft pastels, rounded cards, modern UI"
        }
        
        style_mod = style_modifiers.get(style, style_modifiers["modern"])
        
        prompt = f"{style_mod}, infographic about: {summary_text[:150]}, data visualization, clean design, high quality"
        
        # URL encode the prompt
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Pollinations.ai direct image URL
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
        
        try:
            response = requests.get(image_url, timeout=60)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image
            return None
        except Exception as e:
            print(f"Error with Pollinations: {str(e)}")
            return None
    
    @staticmethod
    def save_infographic(image, video_id, output_dir="static/infographics"):
        """Saves the generated infographic."""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{video_id}_infographic.png")
        image.save(filepath, "PNG", quality=95)
        return filepath


# New: Bria.ai Generator (High Quality)
class BriaInfographicGenerator:
    """
    Uses Bria.ai API for elite-quality infographic generation.
    Supports high-resolution, commercial-grade visual content.
    """
    
    def __init__(self):
        self.api_token = Config.BRIA_API_KEY
        self.base_url = "https://engine.prod.bria-api.com/v2"
        # Base model endpoint
        self.endpoint = f"{self.base_url}/text-to-image/base"
        
    def generate_infographic(self, summary_text, infographic_data=None, style="notebooklm"):
        """
        Generates an infographic using Bria.ai.
        """
        if not self.api_token:
            print("Bria API token missing")
            return None

        # Process dynamic data
        title = "Video Insights"
        interface = "Modern Application"
        themes = "Insight, Strategy, Innovation"
        
        if infographic_data:
            title = infographic_data.get("title", title)
            interface = infographic_data.get("interface", interface)
            themes = infographic_data.get("themes", themes)

        style_prompts = {
            "notebooklm": f"""A professional, clean, modern business infographic layout titled '{title}'. 
                           The design uses a flat vector illustration style with a soft pastel mint-green background. 
                           The layout is organized into a two-column grid. On the left side, include a large data 
                           visualization section featuring a colorful donut chart and a flowing, multi-layered wavy area graph. 
                           In the center, a high-quality smartphone mockup displaying a {interface}. 
                           On the right side, multiple small panels featuring minimalist icons for {themes}. 
                           Use a vibrant color palette of coral red, lime green, and electric blue. 
                           The typography should be bold, sans-serif, and highly legible. 
                           The overall aesthetic is 'Corporate Memphis' but refined, professional, and data-driven. 
                           2D digital art, high resolution, minimalist and scannable.""",
            "modern": "modern flat design infographic, vibrant gradients, clean geometric cards",
            "minimalist": "minimalist professional infographic, white space, simple line icons"
        }
        
        prompt = style_prompts.get(style, style_prompts["notebooklm"])

        negative_prompt = "text, words, letters, paragraphs, messy, cluttered, photograph, realistic, low quality, blurry"

        headers = {
            "api_token": self.api_token
        }
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": "16:9",
            "model": "bria-2.3",
            "sync_mode": False
        }

        try:
            # Bria V2+ is often asynchronous
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                status_url = data.get("status_url")
                
                if not status_url:
                    # Maybe it returned the image directly in sync_mode or different version
                    image_url = data.get("result", {}).get("url")
                    if image_url:
                        img_res = requests.get(image_url, timeout=30)
                        return Image.open(BytesIO(img_res.content))
                    return None

                # Poll for completion
                max_retries = 10
                for _ in range(max_retries):
                    status_res = requests.get(status_url, headers=headers, timeout=20)
                    if status_res.status_code == 200:
                        status_data = status_res.json()
                        if status_data.get("status") == "completed":
                            result_data = status_data.get("result", {})
                            image_url = result_data.get("urls", [None])[0] or result_data.get("url")
                            
                            if image_url:
                                img_res = requests.get(image_url, timeout=30)
                                return Image.open(BytesIO(img_res.content))
                            break
                        elif status_data.get("status") == "failed":
                            print(f"Bria generation failed: {status_data.get('error')}")
                            break
                    time.sleep(5)
            else:
                print(f"Bria API error: {response.status_code} - {response.text}")
                
            return None
        except Exception as e:
            print(f"Exception in Bria generator: {str(e)}")
            return None

    def save_infographic(self, image, video_id, output_dir="static/infographics"):
        """Saves the generated infographic."""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{video_id}_infographic.png")
        image.save(filepath, "PNG", quality=95, optimize=True)
        return filepath

    def generate_and_save(self, summary_text, video_id, infographic_data=None, style="notebooklm"):
        """Complete workflow."""
        image = self.generate_infographic(summary_text, infographic_data, style)
        if image:
            return self.save_infographic(image, video_id)
        return None


# Fallback: Hugging Face (Good free tier)
class HuggingFaceGenerator:
    def __init__(self):
        self.hf_api_key = Config.HUGGINGFACE_API_KEY
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        self.headers = {"Authorization": f"Bearer {self.hf_api_key}"}
    
    def generate_infographic(self, summary_text, style="modern"):
        """Generates using HuggingFace as fallback."""
        style_prompts = {
            "modern": "modern flat design, vibrant colors",
            "minimalist": "minimalist design, clean typography",
            "colorful": "colorful infographic, gradient backgrounds",
            "professional": "professional business infographic, corporate style",
            "notebooklm": "NotebookLM style, soft pastels, rounded design"
        }
        
        style_mod = style_prompts.get(style, style_prompts["modern"])
        prompt = f"{style_mod}, infographic about: {summary_text[:200]}, visual data presentation, clean design"
        
        negative_prompt = "text, words, watermark, blurry, low quality"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            return None
        except Exception as e:
            print(f"HuggingFace error: {str(e)}")
            return None