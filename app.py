import os
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from config import Config
from transcript_processor import TranscriptProcessor
from vector_store_manager import VectorStoreManager
from rag_engine import RAGEngine
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Session
Session(app)

# Initialize Managers
vs_manager = VectorStoreManager()
rag_engine = RAGEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    # Only allow access if a video is being processed
    if 'video_id' not in session:
        return jsonify({"error": "No video processed"}), 400
    return render_template('chat.html')

@app.route('/api/process-video', methods=['POST'])
def process_video():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
        
    video_id = TranscriptProcessor.extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400
        
    try:
        # Fetch metadata and transcript
        metadata = TranscriptProcessor.get_metadata(video_id)
        transcript = TranscriptProcessor.get_transcript(video_id)
        
        # Create a unique session identifier for vector store
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            
        # Create vector store for this session
        vs_manager.create_vector_store(transcript, session['session_id'])
        
        # Store metadata in session
        session['video_id'] = video_id
        session['video_metadata'] = metadata
        
        return jsonify({
            "status": "success",
            "video_id": video_id,
            "metadata": metadata
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
        
    if 'session_id' not in session:
        return jsonify({"error": "Session expired or no video processed"}), 401
        
    try:
        # Load vector store for session
        vector_store = vs_manager.load_vector_store(session['session_id'])
        if not vector_store:
            return jsonify({"error": "Vector store not found. Please re-process the video."}), 404
            
        # Get answer from RAG engine
        answer = rag_engine.get_answer(vector_store, question)
        
        return jsonify({
            "answer": answer
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video-metadata', methods=['GET'])
def get_video_metadata():
    if 'video_metadata' in session:
        return jsonify(session['video_metadata'])
    return jsonify({"error": "No video metadata found"}), 404

@app.route('/api/clear-session', methods=['DELETE'])
def clear_session():
    if 'session_id' in session:
        vs_manager.delete_vector_store(session['session_id'])
    session.clear()
    return jsonify({"status": "session cleared"})

if __name__ == '__main__':
    app.run(debug=True)