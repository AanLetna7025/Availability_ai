# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from chatbot_core.agent import initialize_graph_agent

load_dotenv()
app = FastAPI(title="Project Chatbot API")

class ChatRequest(BaseModel):
    query: str

@app.post("/chat/{project_id}")
async def chat_with_project(project_id: str, request: ChatRequest):
    """
    Chat endpoint for a specific project using a LangGraph agent.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        graph = initialize_graph_agent(project_id)
        
        # Initialize state with required fields
        inputs = {
            "input": request.query,
            "intermediate_steps": [],
            "agent_outcome": "",
            "final_answer": ""
        }
        
        # Invoke the graph
        response = graph.invoke(inputs)
        
        # Extract final answer
        final_response = response.get('final_answer', 'No answer generated')
        
        return {"response": final_response}
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))