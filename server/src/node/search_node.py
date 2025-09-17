import os
import logging
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from server.utils.state import State
from server.service.llm_svc import llm
from server.src.systemmessage import search_prompt
from langchain_community.tools import DuckDuckGoSearchRun



search = DuckDuckGoSearchRun()

async def search_agent(state: State):
    user_query = state["messages"][-1].content
    
    try:
        search_result = await search.ainvoke(user_query)


        system_prompt = SystemMessage(
            content=search_prompt
        )
        messages_to_send = (
            [system_prompt] + 
            state["messages"] + 
            [HumanMessage(content=f"Search results:\n{search_result}")]
        )

        result = await llm.ainvoke(messages_to_send)
        msg = result.content.strip().strip('"')
        # logging.info(f"===filter_agent===\n{result}")
        print(f"\n===search_agent===\n{msg}")

        return {"messages": [result], "state":state}
    except Exception as e:
        logging.exception("An error occurred in search_agent:")
        error_message = HumanMessage(content=f"Error in search step: {str(e)}")
        new_messages = state["messages"] + [error_message]
        return {"messages": new_messages}