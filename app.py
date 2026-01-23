import os 
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough , RunnableParallel ,RunnableLambda
from langchain_core.output_parsers import StrOutputParser

video_id = "QCX62YJCmGk"  # only the ID, not full URL

try:
    # Create API instance
    ytt_api = YouTubeTranscriptApi()

    # Fetch transcript - returns the "best" available transcript
    transcript_list = ytt_api.fetch(video_id, languages=["en"])

    # Flatten it to plain text
    transcript = " ".join(item.text for item in transcript_list)
    # print(transcript)

except TranscriptsDisabled:
    print("No captions available for this video.")
except Exception as e:
    print(f"Error: {e}")

    # creating the chunks of the text 

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])

# creating the embeddings 
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# creating the vector store 
vector_store = FAISS.from_documents(chunks, embeddings)
query = "Why does sugar cause light to twist?"
docs = vector_store.similarity_search(query)
print(docs[0].page_content)
