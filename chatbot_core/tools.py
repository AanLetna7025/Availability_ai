# chatbot_core/tools.py

import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pymongo.uri_parser import parse_uri
from datetime import datetime

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
    Fetches the availability of a user for a specific project from the database.
    """
    try:
        user_oid = ObjectId(user_id)
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid ID format: {e}"}

    # Check if the user is a member of the project
    project = db.invite_users.find_one({"project_id": project_oid, "user_id": user_oid})
    if not project:
        return {"error": "User is not a member of this project"}

    # Get the user's bookings
    bookings = list(db.user_bookings.find({"user_id": user_oid}))

    if not bookings:
        return {"availability": "User has no bookings and is fully available."}

    availability = {}
    for booking in bookings:
        date = booking.get("date").strftime("%Y-%m-%d")
        if date not in availability:
            availability[date] = []

        for session in booking.get("availability_booking_session", []):
            availability[date].append({
                "session_id": str(session.get("session_id")),
                "available": session.get("available")
            })

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

def get_project_status_tool(project_id: str) -> dict:
    """
    Fetches the status of a project from the database.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    tasks = list(db.tasks.find({"project_id": project_oid}))
    total_tasks = len(tasks)
    completed_tasks = 0
    overdue_tasks = 0

    for task in tasks:
        if task.get("status") == "completed":
            completed_tasks += 1
        if task.get("end_date") and task.get("end_date") < datetime.now() and task.get("status") != "completed":
            overdue_tasks += 1

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks
    }
