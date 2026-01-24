import os 
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough , RunnableParallel ,RunnableLambda
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

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

# Reteriever 
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

llm = ChatGroq(
    groq_api_key=os.environ.get("GROK_API_KEY"),
    model_name="llama-3.1-8b-instant", 
    temperature=0.2
)

#creating the promopt 
prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables = ['context', 'question']
)

def format_docs(retrieved_docs):
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context_text

#creating the chains 
parallel_chain = RunnableParallel ({
    'question': RunnablePassthrough(),
    "context": retriever | RunnableLambda(format_docs)
})
parser = StrOutputParser()

main_chain = parallel_chain | prompt | llm | parser

response = main_chain.invoke("summarize into 100 words")
print(response)