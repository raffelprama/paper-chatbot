
# mcp_terminal_chat.py
import os
from dotenv import load_dotenv


import re
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage

from server.src.node.pdf_node import pdf_agent

memory = InMemorySaver()


async def build_graph():
    """
    Build a LangGraph that:
      - uses your OpenAI-compatible model (custom base_url + key)
      - streams tokens & shows tool usage in the terminal
    """
    # INITIATE
    builder = StateGraph(MessagesState)
    builder.add_node("pdf_agent", pdf_agent)

    # FLOW
    builder.add_edge(START, "pdf_agent")
    builder.add_edge("pdf_agent", END)
    graph = builder.compile(checkpointer=memory)
    return graph

from langchain_core.messages import HumanMessage
import asyncio
import json

async def ainvoke():
    APP_GRAPH = await build_graph()
    message="What strategies did Gao et al. (2022) suggest for handling text-to-SQL tasks in large-scale applications?"

    data = await APP_GRAPH.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": 1 or "test-thread"}},
        )
    return {"response": data["messages"][-1].content}
    
if __name__ == "__main__":
    result = asyncio.run(ainvoke())
    final = json.dumps(result, indent=2)
    print(f"\n ===ANSWER===\n{json.dumps(result, indent=2)}")

