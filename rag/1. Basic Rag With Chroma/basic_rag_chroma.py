import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that answers questions based on the provided context. Use the following context to answer the question. If the context does not contain the answer, say you don't know."),
    ("human", "Context: {context}\n\nQuestion: {question}")
])

answer_llm = ChatOllama(model="llama3.2:1b", temperature=0.1)

def load_documents(docs_path="docs"):
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

def ask_llm(question,context):
    chain = prompt | answer_llm | StrOutputParser()
    response = chain.invoke({"context": context, "question": question})
    return response

def main():
    docs_path = "docs"
    persist_directory = "db"
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    if os.path.exists(persist_directory):
        print(f"Loading existing vector store from {persist_directory}...")
        vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    else:
        print("Creating new vector store...")
        documents = load_documents(docs_path)
        chunks = split_documents(documents)
        vector_store = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_directory)

    # Now perform the search
    query = "Type of BOM? Show me some example."
    relevant_docs = vector_store.similarity_search(query, k=2)
    
    context = "\n".join([doc.page_content for doc in relevant_docs])
    response = ask_llm(query, context)
    
    print("\nResponse:")
    print(response)

if __name__ == "__main__":
    main()