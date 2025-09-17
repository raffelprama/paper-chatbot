from server.src.agent.agent import build_graph
from langchain_core.messages import HumanMessage
import asyncio
import json

async def ainvoke():
    APP_GRAPH = await build_graph()
    message="What method did Gan et al. (2022) propose to improve compositional generalization in text-to-SQL?"

    data = await APP_GRAPH.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": 1 or "test-thread"}},
        )
    return {"response": data["messages"][-1].content}
    
if __name__ == "__main__":
    result = asyncio.run(ainvoke())
    final = json.dumps(result, indent=2)
    print(f"\n ===ANSWER===\n{json.dumps(result, indent=2)}")

