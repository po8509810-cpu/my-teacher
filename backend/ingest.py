import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data"
CHROMA_DIR = "chroma_db"

def ingest():
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY is not set in the .env file.")
        return

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created '{DATA_DIR}' directory. Please add some .txt files and run again.")
        return

    # Load documents
    print(f"Loading text files from '{DATA_DIR}'...")
    loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()

    if not documents:
        print(f"No documents found in the '{DATA_DIR}' directory.")
        return

    # Split text
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Create vector database
    print("Creating embeddings and saving to Vector DB...")
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
    
    print(f"Success! Ingestion complete. Database persisted to '{CHROMA_DIR}'.")

if __name__ == "__main__":
    ingest()
