from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver
from server.src.node.search_node import search_agent

memory = InMemorySaver()


async def build_graph():
    """
    Build a LangGraph that:
      - uses your OpenAI-compatible model (custom base_url + key)
      - streams tokens & shows tool usage in the terminal
    """
    # INITIATE
    builder = StateGraph(MessagesState)
    builder.add_node("search_agent", search_agent)

    # FLOW
    builder.add_edge(START, "search_agent")
    builder.add_edge("search_agent", END)
    graph = builder.compile(checkpointer=memory)
    return graph

from langchain_core.messages import HumanMessage
import asyncio
import json

async def ainvoke():
    APP_GRAPH = await build_graph()
    message = "What are the latest developments in artificial intelligence in 2024?"

    data = await APP_GRAPH.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": 1 or "test-thread"}},
        )
    return {"response": data["messages"][-1].content}
    
if __name__ == "__main__":
    result = asyncio.run(ainvoke())
    final = json.dumps(result, indent=2)
    print(f"\n ===ANSWER===\n{json.dumps(result, indent=2)}")
