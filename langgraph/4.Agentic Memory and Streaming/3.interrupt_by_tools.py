from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from ddgs import DDGS
import requests

memory = MemorySaver()

CONFIRM_MESSAGES = {
    "get_weather": lambda args: f"Do you want me to check weather for {args.get('location')}?",
    "research_info": lambda args: f"Do you want me to search online for '{args.get('query')}'?"
}

@tool
def get_weather(location: str) -> str:
    """
    Get current weather for a given city.
    Args:
        location: City name (e.g., "Tokyo", "London")
    """
    url = f"https://wttr.in/{location}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
    # return f"The weather in {location} is currently 22°C and Sunny (Simulated Data)."

@tool
def research_info(query: str) -> str:
    """
    Search online information using DuckDuckGo.
    Args:
        query: Search query string
    """
    results = DDGS().text(query)
    if not results: return "No results found"
    
    formatted_results = [f"Search results for: {query}\n"]
    for i, result in enumerate(results, 1):
        text = f"{i}. {result.get('title')}\n{result.get('body')}\n{result.get('href')}"
        formatted_results.append(text)
    return "\n\n".join(formatted_results)

all_tools = [get_weather, research_info]
llm = ChatOllama(model='qwen3:1.7b').bind_tools(all_tools) # 1.7b对Tool Call支持较差，建议7b

class BasicState(TypedDict): 
    messages: Annotated[list, add_messages]

def call_model(state: BasicState): 
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def human_approval(state: BasicState):
    """审批节点：使用 interrupt 暂停程序并等待输入"""
    last_message = state["messages"][-1]
    
    # 检查是否有工具调用
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name in CONFIRM_MESSAGES:
            # 这里的 interrupt 会挂起程序，直到用户下一次 invoke(resume=...)
            confirm_text = CONFIRM_MESSAGES[tool_name](tool_args)
            user_input = interrupt(confirm_text) 
            
            # 处理用户回答
            if user_input.lower() in ["yes", "y", "sure", "ok"]:
                return Command(goto="tools") # 用户同意，去执行工具
            else:
                # 用户拒绝，插入一条拒绝消息，直接结束或跳回模型
                return Command(
                    update={"messages": [HumanMessage(content="User declined this action.")]},
                    goto=END
                )
    
    return Command(goto=END)

# 5. 构建图
builder = StateGraph(BasicState)
builder.add_node("model", call_model)
builder.add_node("human_approval", human_approval)
builder.add_node("tools", ToolNode(tools=all_tools))

builder.add_edge(START, "model")

# 根据模型输出决定去向
def router(state: BasicState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "human_approval"
    return END

builder.add_conditional_edges("model", router)
builder.add_edge("tools", "model")

app = builder.compile(checkpointer=memory)

# 6. 交互循环
# 注意：thread_id 必须固定才能找回挂起的任务
config = {"configurable": {"thread_id": "user_session_123"}}

print("--- AI Assistant Started ---")
user_query = "What is the current temperature in Tokyo?"

initial_input = {"messages": [HumanMessage(content=user_query)]}

current_input = initial_input

while True:
    # 运行图
    # 注意：如果 current_input 是 Command，invoke 会自动找回 checkpoint 并继续
    result = app.invoke(current_input, config=config)

    # 检查状态快照
    snapshot = app.get_state(config)
    
    if snapshot.next: # 处于中断状态 (human_approval 节点)
        # 获取中断信息
        interrupt_info = snapshot.tasks[0].interrupts[0].value
        print(f"\nSYSTEM: {interrupt_info}")
        
        user_reply = input(">> ")
        
        # 【关键修正】：恢复时只发送 Command，不再发送 initial_input
        current_input = Command(resume=user_reply)
        continue

    # 如果运行结束 (snapshot.next 为空)
    print("\nFINAL RESPONSE:")
    # 打印最后一条消息（通常是模型根据工具结果生成的总结）
    final_msg = result["messages"][-1]
    print(final_msg.content if final_msg.content else "[Tool Call Triggered but no text response]")
    break