import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage,HumanMessage, AIMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the following priority to answer: "
               "1. Use the provided Context if it has the answer. "
               "2. Use the Chat History if the user is asking about previous messages. "
               "3. If neither has the answer, just say you don't know."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "Context: {context}\n\nQuestion: {question}")
])

current_file_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the 'rag' root
# This will be '.../rag'
project_root = os.path.abspath(os.path.join(current_file_dir, ".."))

def load_documents(docs_path=None):
    if docs_path is None:
        docs_path = os.path.join(project_root, "1. Basic Rag With Chroma", "docs")

    # Load documents from the "data" directory
    loader = DirectoryLoader(
        path=os.path.join(os.getcwd(), docs_path),
        glob='**/*.txt',
        loader_cls=TextLoader)
    
    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(f"No documents found in the directory: {docs_path}")
    
    print(f"Loaded {len(documents)} documents from {docs_path}")
    return documents

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    # Split documents into smaller chunks
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)
    
    print(f"Split documents into {len(chunks)} chunks")
    return chunks

def create_vector_store(persist_directory, chunks, embedding_model="ollama"):
    # Create a vector store using Chroma
    if embedding_model == "openai":
        embeddings = OpenAIEmbeddings()
    elif embedding_model == "ollama":
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
    else:
        raise ValueError("Unsupported embedding model. Choose 'openai' or 'ollama'.")

    try:
        vector_store = Chroma.from_documents(
                chunks,
                embeddings, 
                persist_directory=persist_directory)
    except Exception as e:
        print(f"Error creating vector store: {e}")
        raise e

    print(f"Created vector store with {len(vector_store)} vectors")
    return vector_store

def connect_db():
    docs_path = os.path.join(project_root, "1. Basic Rag With Chroma", "docs")
    persist_directory = os.path.join(project_root, "1. Basic Rag With Chroma", "db")
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    if os.path.exists(persist_directory):
        print(f"Loading existing vector store from {persist_directory}...")
        vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        return vector_store
    else:
        print("Creating new vector store...")
        documents = load_documents(docs_path)
        chunks = split_documents(documents)
        vector_store = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_directory)
        return vector_store
    
def ask_llm(question,context,llm,chat_history=None):
    chain = prompt | llm | StrOutputParser()

    print(f"DEBUG: History contains {len(chat_history) if chat_history else 0} messages")

    response = chain.invoke({
        "context": context, 
        "question": question,
        "history": chat_history or []
        })
    return response