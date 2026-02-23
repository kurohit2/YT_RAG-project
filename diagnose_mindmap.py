import os
import sys

# Ensure we are in the right directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from mindmap_generator import GeminiMindMapGenerator
    print("Successfully imported GeminiMindMapGenerator")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

def diagnose():
    try:
        print("Initializing generator...")
        generator = GeminiMindMapGenerator()
        print(f"Generator initialized with model: {generator.model_id}")
        
        test_text = "The universe is a vast expanse of space and time."
        print("Attempting to generate mind map...")
        result = generator.generate_mindmap(test_text)
        
        if result:
            print("Mind map generated successfully!")
            print("Output preview:")
            print(result[:100] + "...")
        else:
            print("Generation returned None (check generator internal errors)")
            
    except Exception as e:
        print(f"Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()
