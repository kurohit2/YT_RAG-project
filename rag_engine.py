import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from config import Config

class RAGEngine:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=Config.GROK_API_KEY,
            model_name=Config.LLM_MODEL,
            temperature=0.2
        )
        self.prompt = PromptTemplate(
            template="""
              You are a helpful assistant.
              Answer ONLY from the provided transcript context.
              If the context is insufficient, just say you don't know politely.

              Context: {context}
              Question: {question}
              
              Answer:
            """,
            input_variables=['context', 'question']
        )
        self.parser = StrOutputParser()

    def get_answer(self, vector_store, question):
        """
        Runs the RAG chain and returns the answer.
        """
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        
        def format_docs(retrieved_docs):
            return "\n\n".join(doc.page_content for doc in retrieved_docs)

        chain = (
            RunnableParallel({
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough()
            })
            | self.prompt
            | self.llm
            | self.parser
        )
        
        return chain.invoke(question)
