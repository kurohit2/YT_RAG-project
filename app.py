import os
from flask import Flask, request, jsonify, render_template, session, send_from_directory
from flask_session import Session
from config import Config
from transcript_processor import TranscriptProcessor
from vector_store_manager import VectorStoreManager
from rag_engine import RAGEngine
from infographic_generator import PollinationsGenerator, HuggingFaceGenerator, BriaInfographicGenerator
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Session
Session(app)

# Initialize Managers
vs_manager = VectorStoreManager()
rag_engine = RAGEngine()
infographic_gen = BriaInfographicGenerator()

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
        session['transcript'] = transcript  # Store for infographic generation
        
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

@app.route('/api/generate-infographic', methods=['POST'])
def generate_infographic():
    """
    Generates an infographic based on video summary using Replicate with fallbacks.
    """
    if 'video_id' not in session:
        return jsonify({"error": "No video processed"}), 400
    
    data = request.json
    style = data.get('style', 'notebooklm')
    model = data.get('model', 'flux-schnell')
    use_fallback = data.get('use_fallback', 'pollinations')
    
    try:
        video_id = session['video_id']
        
        # Get a summary of the video first
        vector_store = vs_manager.load_vector_store(session['session_id'])
        if not vector_store:
            return jsonify({"error": "Vector store not found"}), 404
            
        summary = rag_engine.get_answer(
            vector_store, 
            "Provide a brief 2-3 sentence summary covering the main topic and key points of this video. Use clear, descriptive language."
        )
        # New High-Quality Flow
        try:
            # Extract high-quality metadata for the prompt
            infographic_data = rag_engine.get_infographic_details(vector_store)
            print(f"Extracted Infographic Data: {infographic_data}")
            
            # Try Bria first (Primary) with the new template
            filepath = infographic_gen.generate_and_save(summary, video_id, infographic_data, style)
            if filepath:
                relative_path = f"/static/infographics/{video_id}_infographic.png"
                return jsonify({
                    "status": "success",
                    "infographic_url": relative_path,
                    "summary": summary,
                    "generator": "bria",
                    "details": infographic_data
                })
        except Exception as bria_error:
            print(f"Bria failed: {str(bria_error)}")

        # Try Replicate second
        try:
            # Replicate removed as per user request to focus on Bria
            pass
        except Exception as replicate_error:
            print(f"Replicate failed: {str(replicate_error)}")
        
        # Fallback to Pollinations or HuggingFace
        if use_fallback == 'pollinations':
            image = PollinationsGenerator.generate_infographic(summary, style)
            if image:
                filepath = PollinationsGenerator.save_infographic(image, video_id)
                relative_path = f"/static/infographics/{video_id}_infographic.png"
                return jsonify({
                    "status": "success",
                    "infographic_url": relative_path,
                    "summary": summary,
                    "generator": "pollinations"
                })
        else:
            hf_gen = HuggingFaceGenerator()
            image = hf_gen.generate_infographic(summary, style)
            if image:
                filepath = PollinationsGenerator.save_infographic(image, video_id)
                relative_path = f"/static/infographics/{video_id}_infographic.png"
                return jsonify({
                    "status": "success",
                    "infographic_url": relative_path,
                    "summary": summary,
                    "generator": "huggingface"
                })
        
        return jsonify({"error": "All infographic generators failed"}), 500
            
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

# Serve static infographics
@app.route('/static/infographics/<path:filename>')
def serve_infographic(filename):
    return send_from_directory(Config.INFOGRAPHICS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
