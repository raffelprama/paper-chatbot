#!/usr/bin/env python3
"""
Test script to verify supervisor agent tools are working correctly.
"""
import asyncio
import sys
import os

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from server.src.node.supervisor_node import supervisor_agent, llm_with_tools
from server.utils.state import State
from langchain_core.messages import HumanMessage

async def test_supervisor_tools():
    """Test if the supervisor agent can call tools properly."""
    
    print("🧪 Testing Supervisor Agent Tools...")
    print("=" * 50)
    
    # Test case 1: Simple question that should trigger PDF agent
    test_state = {
        "messages": [
            HumanMessage(content="What is the main finding of the research papers?")
        ]
    }
    
    print("📝 Test Case 1: Basic question")
    print(f"Input: {test_state['messages'][0].content}")
    print("\n🔄 Processing...")
    
    try:
        result = await supervisor_agent(test_state)
        print(f"\n✅ Result: {result}")
        
        # Check if tool calls are present
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                print(f"🎯 Tool calls detected: {[call['name'] for call in last_message.tool_calls]}")
            else:
                print("❌ No tool calls detected in response")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test case 2: Test direct LLM with tools
    print("📝 Test Case 2: Direct LLM tool test")
    
    try:
        messages = [
            HumanMessage(content="Please search the PDF documents for information about machine learning.")
        ]
        
        response = await llm_with_tools.ainvoke(messages)
        print(f"✅ LLM Response: {response}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🎯 Tool calls in LLM response: {[call['name'] for call in response.tool_calls]}")
        else:
            print("❌ No tool calls in LLM response")
            
    except Exception as e:
        print(f"❌ Error in LLM test: {e}")

if __name__ == "__main__":
    asyncio.run(test_supervisor_tools())
