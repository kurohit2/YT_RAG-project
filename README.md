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
Create a `.env` file in the root directory:
```env
GROK_API_KEY=your_groq_api_key_here
FLASK_SECRET_KEY=generate_a_random_string_here
```

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

## Project Structure
- `app.py`: Flask entry point and routes.
- `config.py`: Configuration and environment management.
- `transcript_processor.py`: Video parsing and transcript fetching.
- `vector_store_manager.py`: FAISS persistence and retrieval.
- `rag_engine.py`: LangChain RAG pipeline logic.
- `templates/`: HTML templates.
- `static/`: Frontend assets (JS/CSS).
