import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiMindMapGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-flash-latest"

    def generate_mindmap(self, transcript_text):
        """
        Generates a Mermaid.js mindmap code from a transcript using the new google-genai SDK.
        """
        prompt = f"""
        Analyze the following YouTube video transcript and create a comprehensive mind map in Mermaid.js syntax.
        
        Guidelines:
        1. Use 'mindmap' as the root keyword.
        2. Create a logical hierarchy of concepts.
        3. Keep nodes concise (max 5-6 words per node).
        4. Focus on the main topic and key takeaways.
        5. Return ONLY the Mermaid.js code block, starting with 'mindmap'.
        6. Do not include markdown code fences (like ```mermaid or ```).
        
        Transcript:
        {transcript_text[:15000]}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            mindmap_code = response.text.strip()
            
            # Clean up if Gemini included markdown fences despite instructions
            if mindmap_code.startswith("```"):
                lines = mindmap_code.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                mindmap_code = "\n".join(lines).strip()
            
            if not mindmap_code.startswith("mindmap"):
                mindmap_code = "mindmap\n" + mindmap_code
                
            return mindmap_code
        except Exception as e:
            print(f"Error generating mindmap: {e}")
            raise e
