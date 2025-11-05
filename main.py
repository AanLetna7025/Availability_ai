# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from chatbot_core.agent import initialize_graph_agent

load_dotenv()
app = FastAPI(title="Project Chatbot API")

class ChatRequest(BaseModel):
    query: str

@app.get("/chat/{project_id}")
async def chat_with_project(project_id: str, request: ChatRequest):
    """
    Chat endpoint for a specific project using a LangGraph agent.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        print(f"\n{'='*60}")
        print(f"📨 NEW QUERY: {request.query}")
        print(f"📁 PROJECT ID: {project_id}")
        print(f"{'='*60}\n")
        
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
        
        print(f"\n{'='*60}")
        print(f"📤 COMPLETE STATE:")
        print(f"Final Answer: {response.get('final_answer', 'No answer generated')}")
        print(f"Intermediate Steps: {len(response.get('intermediate_steps', []))} steps")
        print(f"{'='*60}\n")
        
        # Extract final answer
        final_response = response.get('final_answer', 'No answer generated')
        
        return {"response": final_response}
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))