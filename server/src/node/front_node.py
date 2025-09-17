import os
import logging
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from server.utils.state import State
from server.service.llm_svc import llm
from server.src.systemmessage import front_prompt


async def front_agent(state: State):
    try:
        system_prompt = SystemMessage(
            content=front_prompt
        )
        messages_to_send = [system_prompt] + state["messages"]


        result = await llm.ainvoke(messages_to_send)
        # logging.info(f"===filter_agent===\n{result}")
        msg = result.content.strip().strip('"')
        print(f"\n===front_agent===\n{msg}")

        return {"messages": [result]}
    except Exception as e:
        logging.exception("An error occurred in front_agent:")
        error_message = HumanMessage(content=f"Error in front step: {str(e)}")
        new_messages = state["messages"] + [error_message]
        return {"messages": new_messages}