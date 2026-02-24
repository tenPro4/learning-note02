from turtle import st

from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage,HumanMessage,AIMessage
from langchain_core.prompts import PromptTemplate

from utils import vector_db

chat_history = []
llm = ChatOllama(model="llama3.2:1b", temperature=0.1)
vector_store = vector_db.connect_db()
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

def start_chat():
    question1 = "Please summarize the information about the bom in 100 words."

    print(f"Question 1: {question1}")

    docs = retriever.invoke(question1)

    print(f"Retrieved {len(docs)} documents for the question.")

    context = "\n\n".join([doc.page_content for doc in docs])

    response1 = vector_db.ask_llm(question1, context, llm, chat_history)
    print(f"Response 1: {response1}")

    chat_history.append(HumanMessage(content=question1))
    chat_history.append(AIMessage(content=response1))

    question2 = "Did you remember my last question?"
    response2 = vector_db.ask_llm(question2, context="", llm=llm, chat_history=chat_history)
    
    print(f"Response 2: {response2}")

def ask_question(user_question):
    # Step 1: Decide if we need to rewrite or if we should skip searching
    # We ask the LLM to provide a searchable version OR signal to skip retrieval.
    rewrite_prompt = [
        ("system", (
            "Given the chat history and a new user question, rewrite the question "
            "to be a standalone search query. "
            "CRITICAL: If the user is asking a meta-question about the conversation "
            "(e.g., 'What did I just say?', 'Did you remember that?'), "
            "return the exact phrase: [NO_SEARCH]"
        )),
    ] + chat_history + [
        ("human", f"New question: {user_question}")
    ]

    # Only attempt rewrite if there is history; otherwise, use original
    if chat_history:
        rewrite_result = llm.invoke(rewrite_prompt).content.strip()
    else:
        rewrite_result = user_question

    # Step 2: Determine Retrieval Strategy
    if "[NO_SEARCH]" in rewrite_result:
        search_question = user_question
        context = "" # Skip the vector store
        print("DEBUG: Skipping search, answering from memory.")
    else:
        search_question = rewrite_result
        print(f"DEBUG: Searching for: {search_question}")
        
        # Find relevant documents
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(search_question)
        print(f"Found {len(docs)} relevant documents.")
        context = "\n\n".join([doc.page_content for doc in docs])

    # Step 3: Create final prompt
    messages = [
        ("system", (
            "You are a helpful assistant. "
            "1. If Context is provided, use it to answer. "
            "2. Use Chat History to handle meta-questions or clarifications. "
            "3. If the answer isn't in either, say you don't know."
        ))
    ] + chat_history + [
        ("human", f"Context: {context}\n\nQuestion: {user_question}")
    ]
    
    result = llm.invoke(messages)
    answer = result.content
    
    # Step 4: Update History
    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=answer))
    
    print(f"Answer: {answer}")
    return answer

def start_chat2():
    while True:
        user_input = input("\nEnter your question (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break
        ask_question(user_input)


if __name__ == "__main__":
    # start_chat()
    start_chat2()
