import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from config import Config

class RAGEngine:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=Config.GROQ_API_KEY,
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

    def get_infographic_details(self, vector_store):
        """
        Extracts structured details (title, themes, interface) for infographic generation.
        Returns a dictionary or None if failed.
        """
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
        
        extraction_prompt = PromptTemplate(
            template="""
              Based on the provided video transcript, extract key details for a professional infographic.
              Respond in valid JSON format only.

              The JSON must contain:
              1. "title": A short, catchy, professional title (max 40 chars).
              2. "interface": A 3-5 word description of what a mobile app interface related to this topic might look like (e.g., "Personal Finance Dashboard", "Educational Progress Chart").
              3. "themes": A comma-separated list of EXACTLY 3 key themes or topics covered (e.g., "Budgeting, Savings, Transparency").

              Context: {context}
              
              JSON Response:
            """,
            input_variables=['context']
        )

        def format_docs(retrieved_docs):
            return "\n\n".join(doc.page_content for doc in retrieved_docs)

        chain = (
            {"context": retriever | RunnableLambda(format_docs)}
            | extraction_prompt
            | self.llm
            | self.parser
        )
        
        try:
            response = chain.invoke({})
            
            # If already a dict, return it
            if isinstance(response, dict):
                return response
                
            # If it's a string, clean and parse
            if isinstance(response, str):
                clean_json = response.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json.replace("```json", "", 1).rsplit("```", 1)[0].strip()
                elif clean_json.startswith("```"):
                    clean_json = clean_json.replace("```", "", 1).rsplit("```", 1)[0].strip()
                return json.loads(clean_json)
                
            return response
        except Exception as e:
            print(f"Error extracting infographic details: {e}")
            return {
                "title": "Video Insights",
                "interface": "Modern Application",
                "themes": "Education, Technology, Innovation"
            }
