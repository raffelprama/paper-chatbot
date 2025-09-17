from fastapi import APIRouter, HTTPException
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
import asyncio
from typing import Optional
from server.schema.langgraph import ChatMessageRequest, ChatMessageResponse, MemoryClearResponse
from server.src.agent.agent import build_graph


router = APIRouter(prefix="/langgraph", tags=["langgraph"])


# Singleton memory lives inside agent module via InMemorySaver. For clearing, rebuild a new saver.
memory = InMemorySaver()
_graph_cache = None


async def _get_graph():
    global _graph_cache
    if _graph_cache is None:
        _graph_cache = await build_graph(memory)
    return _graph_cache


@router.post("/chatmessage", response_model=ChatMessageResponse)
async def chatmessage(prompt: str):
    """
    Send a prompt to the LangGraph multi-agent system and receive a response.

    Body params:
      - prompt (str): The question or instruction to process.

    Returns a JSON object containing the model's response text. Newlines are
    preserved in the response body.
    """
    try:
        graph = await _get_graph()
        thread = "default-thread"
        data = await graph.ainvoke(
            {"messages": [HumanMessage(content=prompt)]},
            config={"configurable": {"thread_id": thread}},
        )
        # Get the response content and ensure proper newline handling
        response_content = data["messages"][-1].content
        return ChatMessageResponse(response=response_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memory", response_model=MemoryClearResponse)
async def clear_all_memory():
    """
    Clear all threads' memory by creating a fresh InMemorySaver and
    recompiling the graph. This will drop all thread states.
    """
    try:
        global memory, _graph_cache
        memory = InMemorySaver()
        _graph_cache = await build_graph(memory)
        return MemoryClearResponse(status="ok", detail="All memory reinitialized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
