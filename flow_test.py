import asyncio
from server.src.agent.agent import build_graph
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

async def test_complete_flow():
    """Test the complete agent flow."""
    
    print("🧪 Testing Complete Agent Flow...")
    print("=" * 60)
    
    # Build the graph
    graph = await build_graph(memory=memory)
    
    # Test input
    test_input = {
        "messages": [HumanMessage(content="What is the main finding of the research papers?")]
    }
    
    print(f"📝 Input: {test_input['messages'][0].content}")
    print("\n🔄 Running graph...")
    
    try:
        # Run the graph with proper config for checkpointer
        result = await graph.ainvoke(
            test_input,
            config={"configurable": {"thread_id": "test-thread"}}
        )
        
        print(f"\n✅ Final Result:")
        print(f"📄 Messages: {len(result.get('messages', []))}")
        
        if result.get('messages'):
            for i, msg in enumerate(result['messages']):
                print(f"\n--- Message {i+1} ---")
                print(f"Type: {type(msg).__name__}")
                if hasattr(msg, 'content'):
                    print(f"Content: {msg.content[:200]}...")
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    print(f"Tool calls: {[call.get('name') for call in msg.tool_calls]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
