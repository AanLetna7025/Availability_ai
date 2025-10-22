# chatbot_core/agent.py

import os
from typing import TypedDict, Annotated, Sequence
import operator
import re

from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_google_genai import GoogleGenerativeAI
from langgraph.graph import StateGraph, END

from .tools import get_project_details_tool

# --- 1. Define the Agent State ---
class AgentState(TypedDict):
    input: str
    agent_outcome: str  # Changed from Sequence[BaseMessage]
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

Use the following format for your thought process:
Question: the input question you must answer
Thought: you should always think about what to do.
Action: the action to take, should be one of [GetProjectDetails]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""
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
        # Check for Final Answer
        final_answer_match = re.search(r'Final Answer:\s*(.+?)(?:\n|$)', output, re.DOTALL)
        if final_answer_match:
            return ("finish", final_answer_match.group(1).strip())
        
        # Extract Action and Action Input
        action_match = re.search(r'Action:\s*(\w+)', output)
        action_input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', output, re.DOTALL)
        
        if action_match and action_input_match:
            action_name = action_match.group(1).strip()
            action_input = action_input_match.group(1).strip()
            thought_match = re.search(r'Thought:\s*(.+?)(?:\n|$)', output)
            thought = thought_match.group(1).strip() if thought_match else ""
            
            return ("continue", (thought, action_name, action_input))
        
        # If parsing fails, return the raw output as final answer
        return ("finish", output)

    # --- 4. Define the Nodes for the Graph ---

    def run_agent(state):
        """The agent's brain - decides the next action"""
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
        """Executes the tools"""
        action_type, action_data = parse_agent_output(state['agent_outcome'])
        
        if action_type == "finish":
            return {"final_answer": action_data}
        
        thought, action_name, action_input = action_data
        
        # Execute the tool
        if action_name in tools_dict:
            try:
                output = tools_dict[action_name](action_input)
            except Exception as e:
                output = f"Error executing tool: {str(e)}"
        else:
            output = f"Unknown tool: {action_name}"
        
        return {
            "intermediate_steps": [((thought, action_name, action_input), str(output))]
        }

    # --- 5. Define the Conditional Edge ---
    def should_continue(state):
        """Decides whether to continue the loop or finish"""
        action_type, _ = parse_agent_output(state['agent_outcome'])
        
        if action_type == "finish" or len(state.get('intermediate_steps', [])) >= 5:
            return "end"
        else:
            return "continue"

    # --- 6. Assemble the Graph ---
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", run_agent)
    workflow.add_node("action", execute_tools)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": "action",  # Still process final answer
        },
    )
    
    workflow.add_edge("action", END)

    app = workflow.compile()
    
    return app