# YouTube Transcript RAG - Flask Web App

A production-ready web application that allows users to chat with any YouTube video by processing its transcript through a RAG (Retrieval-Augmented Generation) pipeline.

## Features
- **Modern UI**: Clean, minimalist design using Tailwind CSS.
- **URL Validation**: Supports multiple YouTube URL formats.
- **Session-Based Cache**: Vector stores are managed per user session.
- **AI-Powered**: Uses LangChain, FAISS, and Groq (Llama 3) for contextual Q&A.
- **Fast Processing**: Efficient transcript extraction and chunking.

## Tech Stack
- **Backend**: Flask 3.x
- **RAG Pipeline**: LangChain, FAISS, HuggingFace Embeddings
- **LLM**: Groq (Llama 3.1 8B)
- **Frontend**: HTML5, Vanilla JS, Tailwind CSS

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd YT_RAG-project
```

### 2. Set up environment variables
Create a `.env` file in the root directory (copy from `.env.example`):
```env
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
BRIA_API_KEY=your_bria_api_key_here
FLASK_SECRET_KEY=generate_a_random_string_here
```

⚠️ **Never commit `.env` file to GitHub!** It's already in `.gitignore`.

### 3. Install dependencies
It is recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```
The app will be available at `http://127.0.0.1:5000/`.

## API Documentation

- `POST /api/process-video`: Extracts transcript and builds vector store.
- `POST /api/ask-question`: Answers questions based on processed video context.
- `GET /api/video-metadata`: Retrieves title and thumbnail for the current video.
- `DELETE /api/clear-session`: Cleans up session data and vector store files.

## Deployment on Render

### Prerequisites
- GitHub repository (public or private)
- Render account (https://render.com)
- API keys from: Groq, HuggingFace, Bria, and a Flask secret key

### Step-by-Step Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```
   ✅ Your `.env` file won't be pushed (it's in `.gitignore`)

2. **Create Render Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the branch to deploy

3. **Configure Environment Variables**
   - In Render dashboard, go to your service → **Environment**
   - Add these environment variables:
     ```
     GROQ_API_KEY=sk-...
     HUGGINGFACE_API_KEY=hf_...
     BRIA_API_KEY=...
     FLASK_SECRET_KEY=your-random-secret-key
     ```
   - Do NOT add these to GitHub (they stay only in Render)

4. **Configure Build & Start Commands**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - Port: 5000 (detected automatically)

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy when you push to GitHub

### Security Best Practices

✅ **Do this:**
- Keep `.env` in `.gitignore` (already configured)
- Use `.env.example` to show required variables
- Set API keys ONLY in Render dashboard
- Use strong `FLASK_SECRET_KEY` (generate: `python -c "import secrets; print(secrets.token_hex(32))"`)

❌ **Don't do this:**
- Never hardcode API keys in code
- Never commit `.env` file
- Never share API keys in GitHub issues/discussions

## Project Structure
- `app.py`: Flask entry point and routes.
- `config.py`: Configuration and environment management.
- `transcript_processor.py`: Video parsing and transcript fetching.
- `vector_store_manager.py`: FAISS persistence and retrieval.
- `rag_engine.py`: LangChain RAG pipeline logic.
- `templates/`: HTML templates.
- `static/`: Frontend assets (JS/CSS).
