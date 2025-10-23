# chatbot_core/agent.py

import os
from typing import TypedDict, Annotated
import operator
import re

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langgraph.graph import StateGraph, END

from .tools import get_project_details_tool

# --- 1. Define the Agent State ---
class AgentState(TypedDict):
    input: str
    agent_outcome: str
    intermediate_steps: Annotated[list[tuple], operator.add]
    final_answer: str

def initialize_graph_agent(project_id: str):
    """
    Initializes a modern, LangGraph-based agent.
    """
    # Initialize LLM and Tools
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    
    llm = GoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=google_api_key)
    
    # Create tools dictionary for easy lookup
    tools_dict = {
        "GetProjectDetails": get_project_details_tool,
    }
    
    tools_description = "\n".join([
        f"- GetProjectDetails: Use this tool to get all details for a specific project, including its tasks. The input must be a single project ID string."
    ])
    
    # --- 2. Create the Agent's Prompt ---
    prompt = PromptTemplate.from_template(
        """You are an AI assistant helping with project management.
You must answer questions about the project with the ID: {project_id}

You have access to the following tools:
{tools}

CRITICAL RULES:
1. You MUST use the correct tool based on the tool description FIRST before answering ANY question about the project
2. Do NOT make up or assume ANY information
3. Do NOT write "Observation:" yourself - the system will provide it after running the tool
4. After writing "Action Input:", STOP immediately and wait for the Observation
5. Only write "Final Answer:" after you have received an Observation with real data

Use the following format EXACTLY:
Question: the input question you must answer
Thought: think about what to do
Action: call the tool you want to use
Action Input: the project ID
[STOP HERE - System will provide Observation]

After receiving the Observation, then:
Thought: analyze the observation
Final Answer: provide the answer based on the observation

Current conversation:
Question: {input}
{agent_scratchpad}

Now begin! Remember: STOP after "Action Input:" and wait for the Observation."""
    )

    # --- 3. Helper Functions ---
    
    def format_agent_scratchpad(intermediate_steps):
        """Format intermediate steps for the prompt"""
        if not intermediate_steps:
            return ""
        
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += f"Thought: {action[0]}\n"
            thoughts += f"Action: {action[1]}\n"
            thoughts += f"Action Input: {action[2]}\n"
            thoughts += f"Observation: {observation}\n"
        return thoughts
    
    def parse_agent_output(output: str):
        """Parse the LLM output to extract action or final answer"""
        print(f"\n=== RAW LLM OUTPUT ===\n{output}\n====================\n")
        
        # Split output by lines and stop at first "Observation:" to prevent hallucination
        lines = output.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_lines.append(line)
            # Stop if LLM tries to write Observation (it shouldn't!)
            if line.strip().startswith('Observation:'):
                print("⚠️ LLM tried to write Observation - stopping it")
                break
        
        cleaned_output = '\n'.join(cleaned_lines)
        
        # Check for Final Answer FIRST (takes priority)
        final_answer_match = re.search(r'Final Answer:\s*(.+?)$', cleaned_output, re.DOTALL | re.IGNORECASE)
        if final_answer_match:
            answer = final_answer_match.group(1).strip()
            # Remove any trailing "Observation:" text if present
            answer = re.split(r'\nObservation:', answer)[0].strip()
            print(f"✅ Found Final Answer: {answer[:100]}...")
            return ("finish", answer)
        
        # Extract Action and Action Input
        action_match = re.search(r'Action:\s*(\w+)', cleaned_output)
        action_input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', cleaned_output, re.DOTALL)
        
        if action_match and action_input_match:
            action_name = action_match.group(1).strip()
            action_input = action_input_match.group(1).strip()
            
            # Clean up action_input - remove any "Observation:" text
            action_input = re.split(r'\nObservation:', action_input)[0].strip()
            action_input = re.split(r'\nThought:', action_input)[0].strip()
            action_input = re.split(r'\nFinal Answer:', action_input)[0].strip()
            
            # Get the thought (the last one before this action)
            thought_matches = re.findall(r'Thought:\s*(.+?)(?:\n|$)', cleaned_output)
            thought = thought_matches[-1].strip() if thought_matches else "Need to get project details"
            
            print(f"📋 Parsed Action: {action_name}")
            print(f"📥 Action Input: {action_input}")
            print(f"💭 Thought: {thought}")
            
            return ("continue", (thought, action_name, action_input))
        
        # If we can't parse anything useful, ask the agent to try again
        print("⚠️ Could not parse valid action - forcing tool call")
        return ("continue", ("I need to get project details", "GetProjectDetails", project_id))

    # --- 4. Define the Nodes for the Graph ---

    def run_agent(state):
        """The agent's brain - decides the next action"""
        print(f"\n🤖 AGENT THINKING...")
        agent_scratchpad = format_agent_scratchpad(state.get('intermediate_steps', []))
        
        prompt_input = {
            "project_id": project_id,
            "tools": tools_description,
            "input": state['input'],
            "agent_scratchpad": agent_scratchpad
        }
        
        formatted_prompt = prompt.format(**prompt_input)
        agent_outcome = llm.invoke(formatted_prompt)
        
        return {"agent_outcome": agent_outcome}

    def execute_tools(state):
        """Executes the tools or processes final answer"""
        action_type, action_data = parse_agent_output(state['agent_outcome'])
        
        if action_type == "finish":
            print(f"\n✅ PROCESSING FINAL ANSWER...")
            print(f"📝 Answer: {action_data}")
            return {"final_answer": action_data}
        
        print(f"\n🔧 EXECUTING TOOLS...")
        thought, action_name, action_input = action_data
        
        # Execute the tool
        if action_name in tools_dict:
            try:
                print(f"🔍 Calling tool: {action_name} with input: {action_input}")
                output = tools_dict[action_name](action_input)
                print(f"\n📊 TOOL OUTPUT (first 500 chars):\n{str(output)[:500]}...\n")
            except Exception as e:
                output = f"Error executing tool: {str(e)}"
                print(f"❌ ERROR: {output}")
        else:
            output = f"Unknown tool: {action_name}. Available tools: {list(tools_dict.keys())}"
            print(f"❌ {output}")
        
        return {
            "intermediate_steps": [((thought, action_name, action_input), str(output))]
        }

    # --- 5. Define the Conditional Edge ---
    def should_continue(state):
        """Decides whether to continue the loop or finish"""
        action_type, _ = parse_agent_output(state['agent_outcome'])
        
        # Check if we've hit the iteration limit
        if len(state.get('intermediate_steps', [])) >= 5:
            print("⚠️ Maximum iterations reached - forcing finish")
            # Extract whatever answer we have
            return "end"
        
        if action_type == "finish":
            print("🏁 Agent finished - has final answer")
            return "end"
        else:
            print("🔄 Continuing to next iteration")
            return "continue"

    # --- 6. Assemble the Graph ---
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", run_agent)
    workflow.add_node("action", execute_tools)

    workflow.set_entry_point("agent")

    # Route to action node for both continue and end
    # The action node will either execute tools or set final_answer
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": "action",  # Still go to action to process final answer
        },
    )
    
    # After action, decide whether to loop back or end
    def after_action(state):
        """Check if we have a final answer"""
        if state.get('final_answer'):
            print("🎯 Final answer set - ending workflow")
            return "end"
        else:
            print("🔄 No final answer yet - looping back to agent")
            return "continue"
    
    workflow.add_conditional_edges(
        "action",
        after_action,
        {
            "continue": "agent",
            "end": END
        }
    )

    app = workflow.compile()
    
    return app