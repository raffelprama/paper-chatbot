from typing import Annotated
import re
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langgraph.graph import MessagesState
import logging
from langchain_core.messages import AIMessage

def create_handoff_tool(*, agent_name: str, description: str | None = None, tool_name: str | None = None):
    name = tool_name or f"transfer_to_{agent_name}"
    description = description or f"Transfer control to {agent_name} to handle the task."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        # Create a tool message to acknowledge the handoff
        tool_message = {
            "role": "tool",
            "content": f"Transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        
        # Return command to go to the specified agent
        return Command(
            goto=agent_name,  
            update={**state, "messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )

    return handoff_tool

# Helpers for routing
def _last_ai_message(messages):
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            return m
    return None

def _extract_route(text: str):
    match = re.search(r"ROUTE\s*=\s*(PDF|SEARCH|FRONT)", text or "", flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def supervisor_router(state: MessagesState):
    try: 
        ai = _last_ai_message(state["messages"]) if state and "messages" in state else None
        content = getattr(ai, "content", "") if ai else ""
        route = _extract_route(content)
        if route == "PDF":
            return "pdf"
        if route == "SEARCH":
            return "search"
        return "front"
    except Exception as e:
        logging.exception("An error occurred in handoff: {e}")
        return "front"