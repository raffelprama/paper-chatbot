import re
import json
from langchain_core.messages import SystemMessage, AIMessage
from server.utils.state import State
from server.service.llm_svc import llm
from langchain_core.messages import HumanMessage
from langgraph.types import Command
import logging
from server.src.systemmessage import supervisor_prompt


def _extract_route(text: str):
    # Expect: ROUTE=PDF | ROUTE=SEARCH | ROUTE=FRONT
    match = re.search(r"ROUTE\s*=\s*(PDF|SEARCH|FRONT)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


async def supervisor_agent(state: State):
    try:
        system_prompt = SystemMessage(
            content=supervisor_prompt
        )

        messages_to_send = [system_prompt] + state["messages"]
        result = await llm.ainvoke(messages_to_send)
        

        content = result.content or ""
        route = _extract_route(content)

        if route:
            user_query = state["messages"][-1].content  # last HumanMessage
            merged_content = f"{user_query} ROUTE={route}"
            result = AIMessage(content=merged_content, additional_kwargs=result.additional_kwargs)

        # Now update messages
        updated_messages = state["messages"] + [result]
        msg = {"messages": updated_messages}
        print(f"\n===supervisor_agent===")
        print(msg["messages"][-1].content)

        if route == "PDF":
            return Command(goto="pdf_agent", update={"messages": updated_messages})
        if route == "SEARCH":
            return Command(goto="search_agent", update={"messages": updated_messages})
        # Default or FRONT
        return Command(goto="front_agent", update={"messages": updated_messages})
    
    except Exception as e:
        logging.exception("An error occurred in supervisor_agent:")
        error_message = HumanMessage(content=f"Error in supervisor step: {str(e)}")
        new_messages = state["messages"] + [error_message]
        return {"messages": new_messages}