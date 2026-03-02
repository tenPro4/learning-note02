from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph, add_messages,END
from langchain_core.messages import HumanMessage

class State(TypedDict):
    messages: Annotated[list,add_messages]

llm = ChatOllama(model='qwen3:1.7b')

def generate_post(state:State):
    return {
        'messages': [llm.invoke(state.get('messages'))]
    }

def review_decision(state:State):
    post_content = state['messages'][-1]

    print(f"Current linkedin post: {post_content}")

    decision = input("Post to LinkedIn Post(yes/no):\n")

    if decision.lower() == "yes":
        return "approved"
    else:
        return "retry"
    
def post(state: State):
    print(f"Post has been approved and it now live in linked")
    return {'messages':[]}

def collect_feedback(state: State):
    user_feedback = input("What should be changed? ")
    return {
        'messages': [HumanMessage(content=f"Please revise based on this feedback: {user_feedback}")]
    }

graph = StateGraph(State)
graph.add_node("generate_post",generate_post)
graph.add_node("post",post)
graph.add_node("collect_feedback",collect_feedback)

graph.add_edge(START,"generate_post")
graph.add_conditional_edges("generate_post",review_decision,{
    "approved": "post",
    "retry": "collect_feedback"
})
graph.add_edge("collect_feedback","generate_post")
graph.add_edge("post",END)

app = graph.compile()

response = app.invoke({
    'messages': [HumanMessage(content="Write the linked post on career growth")]
})

print(response)