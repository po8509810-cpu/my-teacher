from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_DIR = "chroma_db"

class ChatRequest(BaseModel):
    message: str
    level: str
    subject: str

class ChatResponse(BaseModel):
    reasoning: str
    teachingContent: str
    practice: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") == "your_openai_api_key_here":
        return ChatResponse(
            reasoning="System error: API Key missing.",
            teachingContent="Please add your OPENAI_API_KEY to the backend/.env file to start using the AI.",
            practice=""
        )

    # Initialize Embeddings and Vector Store
    embeddings = OpenAIEmbeddings()
    
    if not os.path.exists(CHROMA_DIR):
        context = "No specific knowledge base context found. The knowledge base is currently empty."
    else:
        try:
            vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
            docs = vectorstore.similarity_search(request.message, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            print(f"Error accessing Vector DB: {e}")
            context = "Failed to access knowledge base."

    # Initialize the LLM with Structured Output to match our Pydantic model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    structured_llm = llm.with_structured_output(ChatResponse)

    prompt_template = """
    You are an AI teacher helping a {level} student learn {subject}.
    Use the following retrieved context from our knowledge base to answer the user's question accurately.
    If the context doesn't contain the answer, rely on your general knowledge but adapt it to the student's level.
    
    Context:
    {context}
    
    User Question: {question}
    """

    prompt = PromptTemplate(
        input_variables=["level", "subject", "context", "question"],
        template=prompt_template,
    )

    # Create chain
    chain = prompt | structured_llm

    try:
        # Generate response matching the ChatResponse structure
        response = chain.invoke({
            "level": request.level,
            "subject": request.subject,
            "context": context,
            "question": request.message
        })
        return response
    except Exception as e:
        print(f"Error during LLM generation: {e}")
        return ChatResponse(
            reasoning="An error occurred while generating the response.",
            teachingContent="I'm sorry, I couldn't process that request properly. Please try again.",
            practice=""
        )
