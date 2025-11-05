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

#helper function to resolve user_id
def _resolve_user_id(user_identifier: str) -> ObjectId:
    """
    Converts user name or ID to ObjectId.
    """
    # Try as ObjectId first
    try:
        return ObjectId(user_identifier)
    except:
        # Search by name
        name_parts = user_identifier.strip().split()
        
        if len(name_parts) == 1:
            # Single name - search first or last name
            query = {
                "$or": [
                    {"first_name": {"$regex": f"^{name_parts[0]}$", "$options": "i"}},
                    {"last_name": {"$regex": f"^{name_parts[0]}$", "$options": "i"}}
                ]
            }
        else:
            # Full name
            query = {
                "$and": [
                    {"first_name": {"$regex": f"^{name_parts[0]}$", "$options": "i"}},
                    {"last_name": {"$regex": f"^{name_parts[-1]}$", "$options": "i"}}
                ]
            }
        
        user = db.users.find_one(query)  # ← Uses db connection from this file
        if not user:
            raise ValueError(f"User '{user_identifier}' not found")
        
        return user['_id']
    
#TOOLS

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

'''def get_project_tasks_tool(project_id: str) -> dict:
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

    return {"tasks": tasks}'''

def get_user_details_tool(user_id: str, project_id: str) -> dict:
    """
    Fetches details for a specific user with skills, roles, and designation resolved. Accepts user ID or name.
    """
    try:
        project_oid = ObjectId(project_id)
        user_oid = _resolve_user_id(user_id)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Invalid ID format: {e}"}

    # Check if user is a member of the project
    membership = db.invite_users.find_one({"project_id": project_oid, "user_id": user_oid})
    if not membership:
        return {"error": "User is not a member of this project"}

    # Aggregation pipeline with lookups
    pipeline = [
        {"$match": {"_id": user_oid}},
        
        # Lookup designation
        {
            "$lookup": {
                "from": "designations",
                "localField": "designation",
                "foreignField": "_id",
                "as": "designation_details"
            }
        },
        
        # Lookup skills
        {
            "$lookup": {
                "from": "skills",
                "localField": "skills",
                "foreignField": "_id",
                "as": "skills_details"
            }
        },
        
        # Lookup roles
        {
            "$lookup": {
                "from": "roles",
                "localField": "roles",
                "foreignField": "_id",
                "as": "roles_details"
            }
        }
    ]

    result = list(db.users.aggregate(pipeline))
    
    if not result:
        return {"error": "User not found"}
    
    user = result[0]
    
    # Convert ObjectId to string
    user['_id'] = str(user['_id'])
    
    # Extract designation name
    if user.get('designation_details') and len(user['designation_details']) > 0:
        user['designation'] = user['designation_details'][0].get('name', 'Unknown')
    else:
        user['designation'] = 'Not set'
    
    # Extract skill names
    if user.get('skills_details'):
        user['skills'] = [skill.get('name', 'Unknown') for skill in user['skills_details']]
    else:
        user['skills'] = []
    
    # Extract role names
    if user.get('roles_details'):
        user['roles'] = [role.get('name', 'Unknown') for role in user['roles_details']]
    else:
        user['roles'] = []
    
    # Clean up - remove the lookup detail fields
    user.pop('designation_details', None)
    user.pop('skills_details', None)
    user.pop('roles_details', None)

    return user

def get_user_availability_tool(user_id: str, project_id: str) -> dict:
    """
    Fetches the availability of a user for a specific project. Accepts user ID or name.
    """
    try:
        project_oid = ObjectId(project_id)
        user_oid = _resolve_user_id(user_id)
    except ValueError as e:
        return {"error": str(e)}
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
    Fetches team members for a specific project with skills, roles, and designation resolved.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    invited_users = list(db.invite_users.find({"project_id": project_oid}))
    team_member_ids = [user['user_id'] for user in invited_users]
    
    if not team_member_ids:
        return {"team_members": [], "message": "No team members found"}

    # Aggregation pipeline with lookups
    pipeline = [
        {"$match": {"_id": {"$in": team_member_ids}}},
        
        # Lookup designation
        {
            "$lookup": {
                "from": "designations",
                "localField": "designation",
                "foreignField": "_id",
                "as": "designation_details"
            }
        },
        
        # Lookup skills
        {
            "$lookup": {
                "from": "skills",
                "localField": "skills",
                "foreignField": "_id",
                "as": "skills_details"
            }
        },
        
        # Lookup roles
        {
            "$lookup": {
                "from": "roles",
                "localField": "roles",
                "foreignField": "_id",
                "as": "roles_details"
            }
        }
    ]

    users = list(db.users.aggregate(pipeline))
    
    team_members = []
    for user in users:
        # Convert ObjectId to string
        user['_id'] = str(user['_id'])
        
        # Extract designation name
        if user.get('designation_details') and len(user['designation_details']) > 0:
            user['designation'] = user['designation_details'][0].get('name', 'Unknown')
        else:
            user['designation'] = 'Not set'
        
        # Extract skill names
        if user.get('skills_details'):
            user['skills'] = [skill.get('name', 'Unknown') for skill in user['skills_details']]
        else:
            user['skills'] = []
        
        # Extract role names
        if user.get('roles_details'):
            user['roles'] = [role.get('name', 'Unknown') for role in user['roles_details']]
        else:
            user['roles'] = []
        
        # Clean up - remove the lookup detail fields
        user.pop('designation_details', None)
        user.pop('skills_details', None)
        user.pop('roles_details', None)
        
        team_members.append(user)

    return {"team_members": team_members, "total": len(team_members)}


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
def get_project_technologies_tool(project_id: str) -> dict:
    """
    Fetches all technologies used in the project with their names, versions, and metadata.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    project = db.projects.find_one({"_id": project_oid})
    if not project:
        return {"error": "Project not found"}

    result = {
        "server_side_technologies": [],
        "client_side_technologies": []
    }

    # Get technologies object from project
    technologies = project.get('technologies', {})
    
    # Process server-side technologies
    server_techs = technologies.get('server', [])
    if server_techs:
        # Extract techIds from the nested structure
        server_tech_ids = [tech.get('techId') for tech in server_techs if tech.get('techId')]
        
        # Batch query for technology details
        tech_docs = list(db.technologies.find({"_id": {"$in": server_tech_ids}}))
        tech_map = {doc['_id']: doc for doc in tech_docs}
        
        # Combine project tech metadata with technology collection data
        for tech in server_techs:
            tech_id = tech.get('techId')
            tech_info = tech_map.get(tech_id)
            
            result["server_side_technologies"].append({
                "id": str(tech_id),
                "name": tech_info.get('name', 'Unknown') if tech_info else 'Unknown',
                "type": tech_info.get('type', 'server') if tech_info else 'server',
                "version": tech.get('version', 'N/A'),
                "note": tech.get('note', ''),
                "reason": tech.get('reason', ''),
                "status": tech.get('status', False)
            })

    # Process client-side technologies
    client_techs = technologies.get('client', [])
    if client_techs:
        # Extract techIds from the nested structure
        client_tech_ids = [tech.get('techId') for tech in client_techs if tech.get('techId')]
        
        # Batch query for technology details
        tech_docs = list(db.technologies.find({"_id": {"$in": client_tech_ids}}))
        tech_map = {doc['_id']: doc for doc in tech_docs}
        
        # Combine project tech metadata with technology collection data
        for tech in client_techs:
            tech_id = tech.get('techId')
            tech_info = tech_map.get(tech_id)
            
            result["client_side_technologies"].append({
                "id": str(tech_id),
                "name": tech_info.get('name', 'Unknown') if tech_info else 'Unknown',
                "type": tech_info.get('type', 'client') if tech_info else 'client',
                "version": tech.get('version', 'N/A'),
                "note": tech.get('note', ''),
                "reason": tech.get('reason', ''),
                "status": tech.get('status', False)
            })

    return result

def get_overdue_tasks_by_user_tool(project_id: str) -> dict:
    """
    Gets all overdue tasks grouped by assigned users.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}
    
    # Find all incomplete tasks past their end date
    overdue_tasks = list(db.tasks.find({
        "project_id": project_oid,
        "task_end_date": {"$lt": datetime.now()},
        "is_task_finished": False
    }))
    
    if not overdue_tasks:
        return {
            "total_overdue_tasks": 0,
            "users_with_overdue_tasks": [],
            "message": "No overdue tasks found for this project."
        }
    
    # Group by user
    user_overdue = {}
    for task in overdue_tasks:
        assigned_users = task.get('assigned_to', [])
        
        # Handle unassigned tasks
        if not assigned_users:
            if 'unassigned' not in user_overdue:
                user_overdue['unassigned'] = {
                    "user_id": None,
                    "user_name": "Unassigned",
                    "overdue_tasks": []
                }
            
            days_overdue = (datetime.now() - task.get('task_end_date')).days
            user_overdue['unassigned']["overdue_tasks"].append({
                "task_id": str(task['_id']),
                "task_name": task.get('task_name'),
                "end_date": task.get('task_end_date').strftime("%Y-%m-%d"),
                "days_overdue": days_overdue,
                "status": task.get('status_name', 'Unknown')
            })
            continue
        
        for user_id in assigned_users:
            user_id_str = str(user_id)
            if user_id_str not in user_overdue:
                # Get user details
                user = db.users.find_one({"_id": user_id})
                user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() if user else "Unknown User"
                user_overdue[user_id_str] = {
                    "user_id": user_id_str,
                    "user_name": user_name,
                    "overdue_tasks": []
                }
            
            days_overdue = (datetime.now() - task.get('task_end_date')).days
            user_overdue[user_id_str]["overdue_tasks"].append({
                "task_id": str(task['_id']),
                "task_name": task.get('task_name'),
                "end_date": task.get('task_end_date').strftime("%Y-%m-%d"),
                "days_overdue": days_overdue,
                "status": task.get('status_name', 'Unknown'),
                "priority": task.get('task_priority', 'Not set')
            })
    
    # Sort users by number of overdue tasks (descending)
    users_list = list(user_overdue.values())
    users_list.sort(key=lambda x: len(x['overdue_tasks']), reverse=True)
    
    return {
        "total_overdue_tasks": len(overdue_tasks),
        "users_with_overdue_tasks": users_list
    }


def get_user_workload_tool(user_id: str, project_id: str) -> dict:
    """
    Gets the workload summary for a specific user in a project. Accepts user ID or name.
    """
    try:
        project_oid = ObjectId(project_id)
        user_oid = _resolve_user_id(user_id)
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Invalid ID format: {e}"}
    
    # Check project membership
    membership = db.invite_users.find_one({"project_id": project_oid, "user_id": user_oid})
    if not membership:
        return {"error": "User is not a member of this project"}
    
    # Get user details
    user = db.users.find_one({"_id": user_oid})
    if not user:
        return {"error": "User not found"}
    
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
    
    # Get all tasks assigned to user
    tasks = list(db.tasks.find({
        "project_id": project_oid,
        "assigned_to": user_oid
    }))
    
    if not tasks:
        return {
            "user_id": user_id,
            "user_name": user_name,
            "total_tasks": 0,
            "message": f"{user_name} has no tasks assigned in this project."
        }
    
    # Categorize tasks
    workload = {
        "user_id": user_id,
        "user_name": user_name,
        "total_tasks": len(tasks),
        "completed_tasks": 0,
        "in_progress_tasks": 0,
        "not_started_tasks": 0,
        "overdue_tasks": 0,
        "tasks_by_status": {},
        "tasks_by_priority": {}
    }
    
    overdue_task_details = []
    upcoming_tasks = []
    
    for task in tasks:
        status = task.get('status_name', 'Unknown')
        priority = task.get('task_priority', 'Not set')
        
        # Count by completion
        if task.get('is_task_finished'):
            workload["completed_tasks"] += 1
        elif task.get('task_end_date') and task.get('task_end_date') < datetime.now():
            workload["overdue_tasks"] += 1
            days_overdue = (datetime.now() - task.get('task_end_date')).days
            overdue_task_details.append({
                "task_name": task.get('task_name'),
                "days_overdue": days_overdue,
                "priority": priority
            })
        elif status in ['In Progress', 'PROGRESS', 'In_Progress']:
            workload["in_progress_tasks"] += 1
        else:
            workload["not_started_tasks"] += 1
        
        # Track upcoming deadlines (next 7 days)
        if task.get('task_end_date') and not task.get('is_task_finished'):
            days_until = (task.get('task_end_date') - datetime.now()).days
            if 0 <= days_until <= 7:
                upcoming_tasks.append({
                    "task_name": task.get('task_name'),
                    "days_until_due": days_until
                })
        
        # Group by status
        if status not in workload["tasks_by_status"]:
            workload["tasks_by_status"][status] = 0
        workload["tasks_by_status"][status] += 1
        
        # Group by priority
        if priority not in workload["tasks_by_priority"]:
            workload["tasks_by_priority"][priority] = 0
        workload["tasks_by_priority"][priority] += 1
    
    # Add additional context
    workload["overdue_task_details"] = overdue_task_details[:5]  # Top 5 overdue
    workload["upcoming_deadlines"] = sorted(upcoming_tasks, key=lambda x: x['days_until_due'])[:5]  # Next 5 deadlines
    
    # Calculate workload percentage
    if workload["total_tasks"] > 0:
        workload["completion_percentage"] = round((workload["completed_tasks"] / workload["total_tasks"]) * 100, 1)
    else:
        workload["completion_percentage"] = 0
    
    return workload

def get_task_details_tool(project_id: str) -> dict:
    """
    Fetches all tasks for a project with user names, milestones, and groups resolved.
    """
    try:
        project_oid = ObjectId(project_id)
    except Exception as e:
        return {"error": f"Invalid Project ID format: {e}"}

    # Aggregation pipeline to join with related collections
    pipeline = [
        {"$match": {"project_id": project_oid}},
        
        # Join with users for assigned_to
        {
            "$lookup": {
                "from": "users",
                "localField": "assigned_to",
                "foreignField": "_id",
                "as": "assigned_user_details"
            }
        },
        
        # Join with users for created_by
        {
            "$lookup": {
                "from": "users",
                "localField": "task_created_by",
                "foreignField": "_id",
                "as": "created_by_details"
            }
        },
        
        # Join with milestones
        {
            "$lookup": {
                "from": "milestones",
                "localField": "milestone_id",
                "foreignField": "_id",
                "as": "milestone_details"
            }
        },
        
        # Join with groups
        {
            "$lookup": {
                "from": "groups",
                "localField": "group_id",
                "foreignField": "_id",
                "as": "group_details"
            }
        }
    ]

    tasks = list(db.tasks.aggregate(pipeline))
    
    if not tasks:
        return {"tasks": [], "message": "No tasks found"}

    results = []
    for task in tasks:
        # Get assigned user names
        assigned_names = []
        if task.get("assigned_user_details"):
            for user in task["assigned_user_details"]:
                name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                assigned_names.append(name or "Unknown")
        
        # Get created by name
        created_by = "Unknown"
        if task.get("created_by_details"):
            user = task["created_by_details"][0]
            created_by = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Unknown"
        
        # Get milestone name
        milestone_name = None
        if task.get("milestone_details"):
            milestone_name = task["milestone_details"][0].get("title")
        
        # Get group name
        group_name = None
        if task.get("group_details"):
            group_name = task["group_details"][0].get("group_name")
        
        # Check if overdue
        is_overdue = False
        if task.get("task_end_date") and not task.get("is_task_finished"):
            is_overdue = task["task_end_date"] < datetime.now()
        
        results.append({
            "task_id": str(task["_id"]),
            "task_name": task.get("task_name"),
            "description": task.get("task_description"),
            "status": task.get("status_name", "Unknown"),
            "priority": task.get("task_priority"),
            "estimate": task.get("estimate"),
            "logged_time": task.get("task_logged_time", "00:00"),
            "start_date": task.get("task_start_date").strftime("%Y-%m-%d") if task.get("task_start_date") else None,
            "end_date": task.get("task_end_date").strftime("%Y-%m-%d") if task.get("task_end_date") else None,
            "is_overdue": is_overdue,
            "is_finished": task.get("is_task_finished", False),
            "assigned_to": ", ".join(assigned_names) if assigned_names else "Unassigned",
            "created_by": created_by,
            "milestone": milestone_name,
            "group": group_name,
        })

    return {"tasks": results, "total": len(results)}