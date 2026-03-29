import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'policies')
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')

def build_vector_store():
    print("1. Loading policy documents...")
    # Loads all .txt files in the data/policies directory
    loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("No documents found. Please add policy .txt files to data/policies/")
        return None

    print(f"Loaded {len(documents)} documents.")

    print("2. Chunking documents...")
    # The Assessment requires you to explain your chunking strategy in the write-up.
    # STRATEGY: RecursiveCharacterTextSplitter is ideal for policies because it tries 
    # to keep paragraphs and sentences together, preserving legal/policy context.
    # Chunk Size: 500 characters (keeps context tight for the LLM).
    # Overlap: 50 characters (prevents cutting off sentences mid-thought).
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    print("3. Generating Embeddings and initializing ChromaDB...")
    # Using a free, open-source embedding model that runs locally
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create the vector store and persist it locally
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_function, 
        persist_directory=CHROMA_DB_DIR
    )
    
    print(f"Success! Vector database saved to {CHROMA_DB_DIR}")
    return vectorstore

def get_retriever():
    """Utility function for your agents to call when they need to search."""
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding_function)
    
    # Return a retriever configured to fetch the top 3 most relevant policy chunks
    return vectorstore.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    # Run this file directly to build the database
    build_vector_store()