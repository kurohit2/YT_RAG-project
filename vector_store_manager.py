import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDINGS_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def create_vector_store(self, transcript, session_id):
        """
        Splits transcript and creates a FAISS vector store saved locally per session.
        """
        chunks = self.splitter.create_documents([transcript])
        vector_store = FAISS.from_documents(chunks, self.embeddings)
        
        path = os.path.join(Config.VECTOR_STORES_DIR, f"vs_{session_id}")
        vector_store.save_local(path)
        return path

    def load_vector_store(self, session_id):
        """
        Loads a saved FAISS vector store for a specific session.
        """
        path = os.path.join(Config.VECTOR_STORES_DIR, f"vs_{session_id}")
        if os.path.exists(path):
            return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        return None

    def delete_vector_store(self, session_id):
        """
        Cleans up vector store files for a session.
        """
        path = os.path.join(Config.VECTOR_STORES_DIR, f"vs_{session_id}")
        if os.path.exists(path):
            import shutil
            shutil.rmtree(path)
