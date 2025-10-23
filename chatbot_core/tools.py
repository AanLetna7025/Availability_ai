# chatbot_core/tools.py

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
    Fetches details for a specific project from the database.
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
        client_id = project['client']
        client_info = db.clients.find_one({"_id": client_id})
        if client_info:
            project['client'] = client_info.get('name', str(client_id))
        else:
            project['client'] = str(client_id)

    return project

def get_project_tasks_tool(project_id: str) -> dict:
    """
    Fetches all tasks for a specific project from the database.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    tasks = list(db.tasks.find({"project_id": project_oid}))
    for task in tasks:
        task['_id'] = str(task['_id'])
        task['project_id'] = str(task['project_id'])
        if task.get('assigned_to'):
            task['assigned_to'] = [str(uid) for uid in task['assigned_to']]

    return {"tasks": tasks}

def get_user_details_tool(user_id: str, project_id: str) -> dict:
    """
    Fetches details for a specific user from the database, but only if they are a member of the specified project.
    """
    try:
        user_oid = ObjectId(user_id)
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid ID format: {e}"}

    project = db.invite_users.find_one({"project_id": project_oid, "user_id": user_oid})
    if not project:
        return {"error": "User is not a member of this project"}

    user = db.users.find_one({"_id": user_oid})
    if not user:
        return {"error": "User not found"}

    user['_id'] = str(user['_id'])
    return user

def get_user_availability_tool(user_id: str, project_id: str) -> dict:
    """
    Fetches the availability of a user from the database, but only if they are a member of the specified project.
    """
    try:
        user_oid = ObjectId(user_id)
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid ID format: {e}"}

    project = db.invite_users.find_one({"project_id": project_oid, "user_id": user_oid})
    if not project:
        return {"error": "User is not a member of this project"}

    availability = list(db.useravailabilitycalender.find({"user_id": user_oid}))
    for item in availability:
        item['_id'] = str(item['_id'])
        item['user_id'] = str(item['user_id'])

    return {"availability": availability}

def get_milestones_tool(project_id: str) -> dict:
    """
    Fetches milestones for a specific project from the database.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    milestones = list(db.milestones.find({"project_id": project_oid}))
    for milestone in milestones:
        milestone['_id'] = str(milestone['_id'])
        milestone['project_id'] = str(milestone['project_id'])

    return {"milestones": milestones}

def get_team_members_tool(project_id: str) -> dict:
    """
    Fetches team members for a specific project from the database.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    invited_users = list(db.invite_users.find({"project_id": project_oid}))
    team_member_ids = [user['user_id'] for user in invited_users]

    team_members = []
    for user_id in team_member_ids:
        user = db.users.find_one({"_id": user_id})
        if user:
            user['_id'] = str(user['_id'])
            team_members.append(user)

    return {"team_members": team_members}
