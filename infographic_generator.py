import os
import requests
from io import BytesIO
from PIL import Image
import replicate
from config import Config

class ReplicateInfographicGenerator:
    """
    Uses Replicate API for high-quality infographic generation.
    Models available: SDXL, Flux, Flux-Pro
    """
    
    def __init__(self):
        self.api_token = Config.REPLICATE_API_TOKEN
        if self.api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token
    
    def generate_infographic(self, summary_text, style="modern", model="flux-schnell"):
        """
        Generates an infographic using Replicate.
        
        Args:
            summary_text: The summarized content from the video
            style: Style of infographic (modern, minimalist, colorful, professional)
            model: Which model to use:
                   - "flux-schnell" (Fast, Free tier friendly)
                   - "flux-dev" (Better quality)
                   - "sdxl" (Stable Diffusion XL)
        
        Returns:
            PIL Image object or None if failed
        """
        
        # Style-specific prompts for NotebookLM-style infographics
        style_prompts = {
            "modern": """modern flat design infographic, clean geometric layout, vibrant gradient colors,
                        minimal icons, rounded corners, contemporary design system, sans-serif typography,
                        data visualization cards, modular grid layout""",
            
            "minimalist": """minimalist infographic design, white and light gray background, 
                           simple line icons, clean sans-serif typography, elegant spacing,
                           subtle shadows, monochromatic color scheme with one accent color,
                           plenty of white space, professional and clean""",
            
            "colorful": """colorful vibrant infographic, gradient backgrounds, playful color palette,
                          bold typography, illustrated icons, dynamic layout, eye-catching design,
                          modern pastel colors, engaging visual elements, fun but professional""",
            
            "professional": """professional business infographic, corporate design, navy blue and white theme,
                              clean structured layout, minimal icons, data charts and graphs,
                              business presentation style, formal typography, credible and trustworthy design""",
            
            "notebooklm": """NotebookLM style infographic, soft pastel color palette, rounded card design,
                           gentle gradients, modern sans-serif fonts, clean information hierarchy,
                           subtle drop shadows, organized sections, contemporary UI design,
                           friendly and approachable aesthetic, light background"""
        }
        
        style_modifier = style_prompts.get(style, style_prompts["notebooklm"])
        
        # Build the complete prompt for infographic generation
        prompt = f"""{style_modifier},
infographic about: {summary_text[:250]},
visual information design, diagram with icons and illustrations,
clear visual hierarchy, organized sections and cards,
professional graphic design, high quality, 8k resolution,
no photographs, vector style graphics, educational illustration,
information architecture, clean composition"""
        
        # Negative prompt to avoid unwanted elements
        negative_prompt = """text, words, letters, paragraphs, written content, watermark, signature, 
blurry, low quality, distorted, ugly, bad anatomy, photograph, realistic photo,
cluttered, messy layout, too much information"""
        
        try:
            # Model selection
            model_versions = {
                "flux-schnell": "black-forest-labs/flux-schnell",  # Fast & Free-tier friendly
                "flux-dev": "black-forest-labs/flux-dev",          # Better quality
                "sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
            }
            
            model_name = model_versions.get(model, model_versions["flux-schnell"])
            
            # Run the model
            output = replicate.run(
                model_name,
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": 1024,
                    "height": 1024,
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 28,
                }
            )
            
            # Download the generated image
            if output:
                image_url = output[0] if isinstance(output, list) else output
                response = requests.get(image_url, timeout=30)
                
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    return image
            
            return None
                
        except Exception as e:
            print(f"Exception in generate_infographic: {str(e)}")
            return None
    
    def save_infographic(self, image, video_id, output_dir="static/infographics"):
        """
        Saves the generated infographic to disk.
        
        Args:
            image: PIL Image object
            video_id: YouTube video ID
            output_dir: Directory to save images
        
        Returns:
            Path to saved image
        """
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, f"{video_id}_infographic.png")
        image.save(filepath, "PNG", quality=95, optimize=True)
        
        return filepath
    
    def generate_and_save(self, summary_text, video_id, style="notebooklm", model="flux-schnell"):
        """
        Complete workflow: generate and save infographic.
        
        Returns:
            Path to saved image or None if failed
        """
        image = self.generate_infographic(summary_text, style, model)
        
        if image:
            filepath = self.save_infographic(image, video_id)
            return filepath
        
        return None


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