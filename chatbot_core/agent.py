from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_google_genai import GoogleGenerativeAI # Import Gemini LLM
from .tools import get_project_details_tool

def initialize_agent(project_id: str):
    """
    Initializes a LangChain agent for a specific project.
    Args:
        project_id (str): The ID of the project for which the agent will answer questions.
    Returns:
        AgentExecutor: An initialized LangChain agent.
    """
    # Initialize your LLM here
    # IMPORTANT: Replace with your actual LLM (e.g., GoogleGenerativeAI, ChatOpenAI)
    # You'll need to set up API keys in your .env file or directly here.
    llm = GoogleGenerativeAI(model="gemini-2.5-flash", temperature=0) # Use Gemini

    tools = [
        Tool(
            name="GetProjectDetails",
            func=lambda pid: get_project_details_tool(pid),
            description="Useful for getting all details about a specific project, including its tasks. Input should be a project ID."
        ),
        # Add more tools here as you create them in tools.py
    ]

    # Define the prompt for the agent
    # This prompt instructs the agent to use the tools to answer questions about the project.
    prompt_template = """
    You are an AI assistant specialized in providing information about a project with ID: {project_id}.
    You have access to the following tools:

    {tools}

    Use the tools to answer questions about the project.
    If the user asks a question that can be answered by the 'GetProjectDetails' tool, use it with the provided project ID.
    If you cannot find an answer using the tools, state that you don't have enough information.

    Question: {input}
    {agent_scratchpad}
    """

    prompt = PromptTemplate.from_template(prompt_template)

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor
