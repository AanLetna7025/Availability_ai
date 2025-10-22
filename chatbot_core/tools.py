from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")

client = MongoClient(MONGO_URI)
db = client.get_database()

def get_project_details_tool(project_id: str) -> dict:
    """
    Fetches details for a specific project from the database.
    Args:
        project_id (str): The ID of the project to fetch.
    Returns:
        dict: A dictionary containing project details, including its tasks.
    """
    try:
        project_oid = ObjectId(project_id)
    except:
        return {"error": "Invalid Project ID format"}

    project = db.projects.find_one({"_id": project_oid})
    if not project:
        return {"error": "Project not found"}

    # Convert ObjectId to string for JSON serialization
    project['_id'] = str(project['_id'])
    if 'client' in project and project['client']:
        project['client'] = str(project['client'])
    
    # Fetch related tasks
    tasks = list(db.tasks.find({"project_id": project_oid}))
    for task in tasks:
        task['_id'] = str(task['_id'])
        task['project_id'] = str(task['project_id'])
        if 'assigned_to' in task and task['assigned_to']:
            task['assigned_to'] = [str(user_id) for user_id in task['assigned_to']]

    project['tasks'] = tasks

    return project
