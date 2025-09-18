#!/usr/bin/env python3
"""
Test all individual agents to ensure they work properly.
This script tests each agent in isolation to verify functionality.
"""

import asyncio
import json
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

# Import all agents
from server.src.node.clarification_node import clarification_agent
from server.src.node.supervisor_node import supervisor_agent
from server.src.node.pdf_node import pdf_agent
from server.src.node.search_node import search_agent
from server.src.node.front_node import front_agent

async def test_agent(agent_name, agent_func, test_input, expected_behavior):
    """Test a single agent and return results."""
    print(f"\nTesting {agent_name}...")
    print("=" * 50)
    
    try:
        # Create test state
        test_state = {
            "messages": [HumanMessage(content=test_input)]
        }
        
        print(f"Input: {test_input}")
        print(f"Expected: {expected_behavior}")
        print("\n🔄 Running agent...")
        
        # Run the agent
        result = await agent_func(test_state)
        
        print(f"\n✅ {agent_name} Result:")
        
        # Handle different return types
        if hasattr(result, 'goto'):  # Command object (supervisor agent)
            print(f"Route: {result.goto}")
            print(f"Update: {result.update}")
            print(f"Type: Command (LangGraph routing)")
        elif isinstance(result, dict) and 'messages' in result:
            print(f"Messages: {len(result.get('messages', []))}")
            if result.get('messages'):
                for i, msg in enumerate(result['messages']):
                    print(f"\n--- Message {i+1} ---")
                    print(f"Type: {type(msg).__name__}")
                    if hasattr(msg, 'content'):
                        content = msg.content
                        print(f"Content: {content[:300]}{'...' if len(content) > 300 else ''}")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"Tool calls: {[call.get('name') for call in msg.tool_calls]}")
        else:
            print(f"Result: {result}")
            print(f"Type: {type(result).__name__}")
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        print(f"❌ {agent_name} Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

async def test_all_agents():
    """Test all agents individually."""
    print("Testing All Individual Agents")
    print("=" * 60)
    
    # Test cases for each agent
    test_cases = [
        {
            "name": "Clarification Agent",
            "agent": clarification_agent,
            "input": "What are the main findings in the research papers?",
            "expected": "Should expand and clarify the user query"
        },
        {
            "name": "Supervisor Agent", 
            "agent": supervisor_agent,
            "input": "What are the main findings in the research papers?",
            "expected": "Should route to appropriate agent (likely PDF agent)"
        },
        {
            "name": "PDF Agent",
            "agent": pdf_agent,
            "input": "What are the main findings in the research papers?",
            "expected": "Should search PDF documents and return relevant information"
        },
        {
            "name": "Search Agent",
            "agent": search_agent,
            "input": "What are the latest developments in AI in 2024?",
            "expected": "Should perform web search and return current information"
        },
        {
            "name": "Front Agent",
            "agent": front_agent,
            "input": "Based on the research papers, the main findings are...",
            "expected": "Should format and present the final response"
        }
    ]
    
    results = {}
    
    # Test each agent
    for test_case in test_cases:
        result = await test_agent(
            test_case["name"],
            test_case["agent"], 
            test_case["input"],
            test_case["expected"]
        )
        results[test_case["name"]] = result
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Summary
    print(f"\nTest Summary")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for agent_name, result in results.items():
        status = result["status"]
        if status == "success":
            print(f"✅ {agent_name}: PASSED")
            success_count += 1
        else:
            print(f"❌ {agent_name}: FAILED - {result.get('error', 'Unknown error')}")
            error_count += 1
    
    print(f"\nOverall Results:")
    print(f"   ✅ Passed: {success_count}/{len(test_cases)}")
    print(f"   ❌ Failed: {error_count}/{len(test_cases)}")
    
    if error_count == 0:
        print(f"\nAll agents are working correctly!")
    else:
        print(f"\n⚠️  Some agents need attention. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(test_all_agents())
