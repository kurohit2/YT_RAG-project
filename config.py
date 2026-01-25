import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-key-12345")
    GROK_API_KEY = os.environ.get("GROK_API_KEY")
    REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
    HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Vector Store Paths
    VECTOR_STORES_DIR = os.path.join(os.getcwd(), 'vector_stores')
    INFOGRAPHICS_DIR = os.path.join(os.getcwd(), 'static', 'infographics')
    
    # Model Configuration
    EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "llama-3.1-8b-instant"

# Ensure directories exist
os.makedirs(Config.SESSION_FILE_DIR, exist_ok=True)
os.makedirs(Config.VECTOR_STORES_DIR, exist_ok=True)
os.makedirs(Config.INFOGRAPHICS_DIR, exist_ok=True)
