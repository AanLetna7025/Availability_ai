# chatbot_core/tools.py
# (No changes needed, this file is correct)

import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pymongo.uri_parser import parse_uri

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")

client = MongoClient(MONGO_URI)
db_name = parse_uri(MONGO_URI)['database']
if not db_name:
    raise ValueError("Database not found in MONGO_URI")
db = client[db_name]

def get_project_details_tool(project_id: str) -> dict:
    """
    Fetches details for a specific project from the database, including its tasks.
    The input to this tool should be a single project ID string.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    project = db.projects.find_one({"_id": project_oid})
    if not project:
        return {"error": "Project not found"}

    project['_id'] = str(project['_id'])
    if project.get('client'):
        project['client'] = str(project['client'])
    
    tasks = list(db.tasks.find({"project_id": project_oid}))
    for task in tasks:
        task['_id'] = str(task['_id'])
        task['project_id'] = str(task['project_id'])
        if task.get('assigned_to'):
            task['assigned_to'] = [str(uid) for uid in task['assigned_to']]

    project['tasks'] = tasks
    return project