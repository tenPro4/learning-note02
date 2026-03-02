from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, add_messages
from langgraph.types import Command, interrupt

memory = MemorySaver()

class State(TypedDict):
    value: str

def node_a(state:State):
    print("current node: node a")
    return Command(
        goto="node_b", 
        update={
            "value": state["value"] + "a"
        }
    )

def node_b(state:State):
    print("current node: node b")

    decision = interrupt({
        "question":"Property define here just for display purpose(like frontend)",
        "details":"You can define as many properties you like for proper message"
    })

    print("Human Review Values: ", decision)

    if decision == "c":
        return Command(
            goto="node_c",
            update={
                'value': state["value"] + "b"
            }
        )
    else:
        return Command(
            goto="node_d",
            update={
                'value': state["value"] + "b"
            }
        )

def node_c(state:State):
    print("current node: node c")
    return Command(
        goto="node_d", 
        update={
            "value": state["value"] + "c"
        }
    )

def node_d(state:State):
    print("current node: node d")
    return Command(
        goto=END, 
        update={
            "value": state["value"] + "d"
        }
    )

graph = StateGraph(State)

graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.add_node("node_d", node_d)


graph.set_entry_point("node_a") 
app = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

initialState = {
    "value": ""
}

first_result = app.invoke(initialState, config, stream_mode="updates")

print(first_result)

second_result = app.invoke(Command(resume=input("What is next?")), config=config, stream_mode="updates")
print(second_result)