import os
import re
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

from server.src.node.pdf_node import pdf_agent
from server.src.node.front_node import front_agent
from server.src.node.search_node import search_agent
from server.src.agent.handoff import supervisor_router
from server.src.node.supervisor_node import supervisor_agent
from server.src.node.clarification_node import clarification_agent

# memory = InMemorySaver()

async def build_graph(memory):
    """
    Build a LangGraph that:
      - uses your OpenAI-compatible model (custom base_url + key)
      - streams tokens & shows tool usage in the terminal
    """
    # INITIATE
    builder = StateGraph(MessagesState)
    builder.add_node("clarification_agent", clarification_agent)
    builder.add_node("supervisor_agent", supervisor_agent, destinations=("pdf_agent", "search_agent","front_agent"))
    builder.add_node("pdf_agent", pdf_agent)
    builder.add_node("front_agent", front_agent)
    builder.add_node("search_agent", search_agent)

    # FLOW
    builder.add_edge(START, "clarification_agent")
    builder.add_edge("clarification_agent", "supervisor_agent")
    builder.add_conditional_edges(
        "supervisor_agent",
        supervisor_router,
        {
            "pdf": "pdf_agent",
            "search": "search_agent",
            "front": "front_agent",
        },
    )
    builder.add_edge("pdf_agent", "supervisor_agent")
    builder.add_edge("search_agent", "supervisor_agent")
    builder.add_edge("front_agent", END)
    graph = builder.compile(checkpointer=memory)
    return graph