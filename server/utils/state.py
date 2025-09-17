from typing import TypedDict, Dict, Annotated

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class State(TypedDict):
    messages: Annotated[list, add_messages]