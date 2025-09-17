import os
import logging
import json
from dotenv import load_dotenv

from langchain_qdrant import QdrantVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.vectorstores import QdrantVectorStore


from server.utils.state import State
from server.service.llm_svc import llm
from server.service.qdrant_svc import qdrant_client
from server.src.systemmessage import pdf_prompt
from langgraph.types import Command


collection = os.getenv("COLLECTION_NAME")
model_e = os.getenv("MODEL_E")
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")

retriever = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection,
    embedding=OpenAIEmbeddings(
        openai_api_base=base_url,
        openai_api_key=api_key,
        model=model_e
        )
).as_retriever(search_kwargs={"k": 10})


prompt = ChatPromptTemplate.from_messages([
    ("system", pdf_prompt + "\n\nContext:\n{context}"),
    ("human", "{question}")
])

async def pdf_agent(state: State):
    try:
        # Extract the latest question or instruction
        last_user_msg = state["messages"][-1].content if state["messages"] else ""

        # Query Qdrant retriever with fallback to web search on failure
        try:
            docs = await retriever.ainvoke(last_user_msg)
            context = "\n\n".join([d.page_content for d in docs]) if docs else "no_results"
        except Exception as e:
            print(f"pdf_agent retriever error: {e}")
            # Fallback: route to search_agent to continue the flow naturally
            return Command(
                goto="search_agent",
                update={
                    "messages": state["messages"]
                    + [HumanMessage(content=f"PDF retrieval failed, falling back to web search. Error: {e}")],
                },
            )

        # Format prompt with question + retrieved context
        messages_to_send = prompt.format_messages(question=last_user_msg, context=context)

        result = await llm.ainvoke(messages_to_send)
        msg = result.content.strip().strip('"')

        print(f"\n===pdf_agent (with retriever)===\n{msg}")
        return {"messages": [result], "next": "supervisor_agent"}
    except Exception as e:
        logging.exception("An error occurred in pdf_agent:")
        error_message = HumanMessage(content=f"Error in pdf step: {str(e)}")
        new_messages = state["messages"] + [error_message]
        return {"messages": new_messages}