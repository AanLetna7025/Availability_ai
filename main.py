# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from chatbot_core.agent import initialize_graph_agent

load_dotenv()

# Cache for graph instances (one per project)
graph_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*60)
    print("🚀 FastAPI Starting Up...")
    print("="*60)
    try:
        # Test MongoDB connection
        from chatbot_core.tools import db
        db.command('ping')
        print("✅ MongoDB connected")
        
        # Test Google API Key
        import os
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            print("✅ Google API Key found")
        else:
            print("⚠️  Google API Key not found!")
            
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n🛑 FastAPI shutting down...")

app = FastAPI(title="Project Chatbot API", lifespan=lifespan)

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8501",
        "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    user_id: str

@app.post("/chat/{project_id}")
async def chat_with_project(project_id: str, request: ChatRequest):
    """
    Chat endpoint with conversation memory per user-project combination.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        print(f"\n{'='*60}")
        print(f"📨 QUERY: {request.query}")
        print(f"👤 USER: {request.user_id}")
        print(f"📁 PROJECT: {project_id}")
        print(f"{'='*60}\n")
        
        # Get or create graph for this project
        if project_id not in graph_cache:
            print(f"🔧 Initializing new graph for project: {project_id}")
            try:
                graph_cache[project_id] = initialize_graph_agent(project_id)
                print(f"✅ Graph initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize graph: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
        
        graph = graph_cache[project_id]
        
        # Unique thread per user-project
        thread_id = f"{request.user_id}_{project_id}"
        
        # Run the agent
        inputs = {
            "input": request.query,
            "intermediate_steps": [],
            "agent_outcome": "",
            "final_answer": ""
        }
        
        print(f"🚀 Invoking agent with thread_id: {thread_id}")
        response = graph.invoke(
            inputs,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 50  # Increase from default 25
            }
        )
        
        final_answer = response.get('final_answer', 'No answer generated')
        
        print(f"\n✅ Response generated: {final_answer[:100]}...\n")
        
        return {
            "response": final_answer,
            "thread_id": thread_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error: {str(e)}")
        print(f"📋 Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
        
    try:
        print(f"\n{'='*60}")
        print(f"📨 QUERY: {request.query}")
        print(f"👤 USER: {request.user_id}")
        print(f"📁 PROJECT: {project_id}")
        print(f"{'='*60}\n")
        
        # Get or create graph for this project
        if project_id not in graph_cache:
            graph_cache[project_id] = initialize_graph_agent(project_id)
        
        graph = graph_cache[project_id]
        
        # Unique thread per user-project
        thread_id = f"{request.user_id}_{project_id}"
        
        # Run the agent
        inputs = {
            "input": request.query,
            "intermediate_steps": [],
            "agent_outcome": "",
            "final_answer": ""
        }
        
        response = graph.invoke(
            inputs,
            config={"configurable": {"thread_id": thread_id}}
        )
        
        final_answer = response.get('final_answer', 'No answer generated')
        
        print(f"\n✅ Response: {final_answer[:100]}...\n")
        
        return {
            "response": final_answer,
            "thread_id": thread_id
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}