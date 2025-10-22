from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson import ObjectId
from chatbot_core.agent import initialize_agent # Import the agent

# Load environment variables
load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")

client = MongoClient(MONGO_URI)
db = client.get_database() # This will get the database specified in the MONGO_URI

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Project Chatbot API"}

# This endpoint is for testing direct project details retrieval, can be removed later
@app.get("/project/{project_id}")
async def get_project_details(project_id: str):
    try:
        project_oid = ObjectId(project_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid Project ID format")

    project = db.projects.find_one({"_id": project_oid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Convert ObjectId to string for JSON serialization
    project['_id'] = str(project['_id'])
    if 'client' in project and project['client']:
        project['client'] = str(project['_id'])
    
    # Fetch related tasks
    tasks = list(db.tasks.find({"project_id": project_oid}))
    for task in tasks:
        task['_id'] = str(task['_id'])
        task['project_id'] = str(task['_id'])
        if 'assigned_to' in task and task['assigned_to']:
            task['assigned_to'] = [str(user_id) for user_id in task['assigned_to']]

    project['tasks'] = tasks

    return project

@app.post("/chat/{project_id}")
async def chat_with_project(project_id: str, query: str):
    """
    Chat endpoint for a specific project.
    Initializes a LangChain agent for the given project_id and processes the user query.
    """
    try:
        # Initialize the agent with the project_id
        agent_executor = initialize_agent(project_id)
        
        # Run the agent with the user's query
        response = agent_executor.invoke({"input": query, "project_id": project_id})
        
        return {"response": response["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))