# chatbot_core/analysis_tools.py

"""
Project analysis tools using your exact MongoDB schema
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Import your existing DB connection
from .tools import db

# ============================================================================
# PROJECT HEALTH ANALYSIS
# ============================================================================

def calculate_project_health(project_id: str) -> Dict[str, Any]:
    """
    Calculate overall project health score (0-100) based on multiple factors.
    
    Scoring breakdown:
    - Completion Rate (40%)
    - Timeline Adherence (30%) 
    - Workload Balance (20%)
    - Team Velocity (10%)
    """
    try:
        project_oid = ObjectId(project_id)
        
        # Verify project exists
        project = db.projects.find_one({"_id": project_oid})
        if not project:
            return {"error": "Project not found"}
        
        # Get all tasks
        all_tasks = list(db.tasks.find({"project_id": project_oid}))
        
        if not all_tasks:
            return {
                "health_score": 0,
                "health_status": "NO_DATA",
                "message": "No tasks found for this project"
            }
        
        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for t in all_tasks if t.get("is_task_finished", False))
        
        # Count overdue tasks
        now = datetime.now()
        overdue_tasks = sum(
            1 for t in all_tasks 
            if t.get("task_end_date") and 
               t["task_end_date"] < now and 
               not t.get("is_task_finished", False)
        )
        
        # Count in-progress tasks
        in_progress = sum(
            1 for t in all_tasks
            if not t.get("is_task_finished", False) and 
               t.get("status_name") not in ["NEW", "COMPLETED"]
        )
        
        # 1. COMPLETION SCORE (40% weight)
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        completion_score = (completion_rate / 100) * 40
        
        # 2. TIMELINE SCORE (30% weight)
        # Penalize heavily for overdue tasks
        overdue_penalty = min(overdue_tasks * 5, 30)  # Max penalty: 30 points
        timeline_score = max(0, 30 - overdue_penalty)
        
        # 3. WORKLOAD BALANCE SCORE (20% weight)
        team_count = db.invite_users.count_documents({
            "project_id": project_oid,
            "status": "active"
        })
        
        if team_count > 0:
            # Check task distribution
            user_task_counts = {}
            for task in all_tasks:
                if not task.get("is_task_finished", False):
                    for user_id in task.get("assigned_to", []):
                        user_id_str = str(user_id)
                        user_task_counts[user_id_str] = user_task_counts.get(user_id_str, 0) + 1
            
            if user_task_counts:
                task_counts = list(user_task_counts.values())
                avg_tasks = sum(task_counts) / len(task_counts)
                # Calculate standard deviation (simple version)
                variance = sum((x - avg_tasks) ** 2 for x in task_counts) / len(task_counts)
                std_dev = variance ** 0.5
                
                # Good balance = low standard deviation
                # Score reduces as std_dev increases
                balance_score = max(0, 20 - (std_dev * 2))
            else:
                balance_score = 10  # Some score if no active tasks
        else:
            balance_score = 0
        
        # 4. VELOCITY SCORE (10% weight)
        # Check if tasks are being completed recently
        week_ago = datetime.now() - timedelta(days=7)
        recent_completions = sum(
            1 for t in all_tasks
            if t.get("is_task_finished", False) and
               t.get("updatedAt") and
               t["updatedAt"] > week_ago
        )
        
        # Good velocity = at least 1 completion per team member per week
        expected_velocity = team_count if team_count > 0 else 1
        velocity_ratio = min(recent_completions / expected_velocity, 1.0) if expected_velocity > 0 else 0
        velocity_score = velocity_ratio * 10
        
        # CALCULATE TOTAL HEALTH
        health_score = round(completion_score + timeline_score + balance_score + velocity_score)
        
        # Determine status
        if health_score >= 80:
            status = "EXCELLENT"
            color = "#22c55e"  # green
            emoji = "🟢"
        elif health_score >= 60:
            status = "GOOD"
            color = "#84cc16"  # lime
            emoji = "🟡"
        elif health_score >= 40:
            status = "AT_RISK"
            color = "#f59e0b"  # amber
            emoji = "🟠"
        else:
            status = "CRITICAL"
            color = "#ef4444"  # red
            emoji = "🔴"
        
        return {
            "health_score": health_score,
            "health_status": status,
            "status_color": color,
            "status_emoji": emoji,
            "breakdown": {
                "completion_score": round(completion_score),
                "timeline_score": round(timeline_score),
                "balance_score": round(balance_score),
                "velocity_score": round(velocity_score)
            },
            "metrics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress,
                "overdue_tasks": overdue_tasks,
                "completion_rate": round(completion_rate, 1),
                "team_size": team_count,
                "recent_completions": recent_completions
            },
            "project_name": project.get("name", "Unknown"),
            "project_status": project.get("status", "unknown")
        }
        
    except Exception as e:
        import traceback
        return {
            "error": f"Failed to calculate health: {str(e)}",
            "traceback": traceback.format_exc()
        }


# ============================================================================
# WORKLOAD ANALYSIS
# ============================================================================

def analyze_team_workload_balance(project_id: str) -> Dict[str, Any]:
    """
    Analyze how work is distributed across the team.
    Identifies overloaded and underutilized team members.
    """
    try:
        project_oid = ObjectId(project_id)
        
        # Get active team members
        team_members = list(db.invite_users.find({
            "project_id": project_oid,
            "status": "active"
        }))
        
        if not team_members:
            return {"error": "No team members found"}
        
        # Get all incomplete tasks
        active_tasks = list(db.tasks.find({
            "project_id": project_oid,
            "is_task_finished": False
        }))
        
        # Analyze workload per person
        workload_data = []
        
        for member in team_members:
            user_id = member["user_id"]
            
            # Get user details
            user = db.users.find_one({"_id": user_id})
            if not user:
                continue
            
            user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            # Count tasks assigned to this user
            user_tasks = [t for t in active_tasks if user_id in t.get("assigned_to", [])]
            
            # Count overdue tasks
            now = datetime.now()
            overdue_count = sum(
                1 for t in user_tasks
                if t.get("task_end_date") and t["task_end_date"] < now
            )
            
            # Calculate total estimated hours
            total_estimate = 0
            for task in user_tasks:
                estimate_str = task.get("estimate", "0")
                if estimate_str and estimate_str != "0":
                    try:
                        # Handle different formats: "8", "8.5", "8:30"
                        if ":" in str(estimate_str):
                            hours, mins = str(estimate_str).split(":")
                            total_estimate += float(hours) + (float(mins) / 60)
                        else:
                            total_estimate += float(estimate_str)
                    except:
                        pass
            
            workload_data.append({
                "user_id": str(user_id),
                "user_name": user_name,
                "email": user.get("email", ""),
                "designation": str(user.get("designation", "")) if user.get("designation") else None,
                "total_tasks": len(user_tasks),
                "overdue_tasks": overdue_count,
                "estimated_hours": round(total_estimate, 1),
                "task_list": [
                    {
                        "task_name": t.get("task_name"),
                        "status": t.get("status_name"),
                        "priority": t.get("task_priority"),
                        "is_overdue": t.get("task_end_date") < now if t.get("task_end_date") else False
                    }
                    for t in user_tasks[:5]  # Top 5 tasks
                ]
            })
        
        # Sort by workload (descending)
        workload_data.sort(key=lambda x: x["total_tasks"], reverse=True)
        
        # Calculate statistics
        task_counts = [w["total_tasks"] for w in workload_data]
        avg_tasks = sum(task_counts) / len(task_counts) if task_counts else 0
        max_tasks = max(task_counts) if task_counts else 0
        min_tasks = min(task_counts) if task_counts else 0
        
        # Identify categories
        overloaded = [w for w in workload_data if w["total_tasks"] > avg_tasks * 1.5]
        balanced = [w for w in workload_data if avg_tasks * 0.5 <= w["total_tasks"] <= avg_tasks * 1.5]
        underutilized = [w for w in workload_data if w["total_tasks"] < avg_tasks * 0.5]
        
        # Determine balance status
        if len(overloaded) > len(team_members) * 0.3:
            balance_status = "IMBALANCED"
            balance_color = "#f59e0b"
        elif len(underutilized) > len(team_members) * 0.3:
            balance_status = "UNDERUTILIZED"
            balance_color = "#3b82f6"
        else:
            balance_status = "BALANCED"
            balance_color = "#22c55e"
        
        return {
            "balance_status": balance_status,
            "balance_color": balance_color,
            "team_size": len(team_members),
            "statistics": {
                "average_tasks_per_person": round(avg_tasks, 1),
                "max_tasks": max_tasks,
                "min_tasks": min_tasks,
                "total_active_tasks": len(active_tasks)
            },
            "categories": {
                "overloaded_count": len(overloaded),
                "balanced_count": len(balanced),
                "underutilized_count": len(underutilized)
            },
            "overloaded_members": overloaded,
            "balanced_members": balanced,
            "underutilized_members": underutilized,
            "all_members": workload_data
        }
        
    except Exception as e:
        import traceback
        return {
            "error": f"Workload analysis failed: {str(e)}",
            "traceback": traceback.format_exc()
        }


# ============================================================================
# BOTTLENECK DETECTION
# ============================================================================

def detect_bottlenecks(project_id: str) -> Dict[str, Any]:
    """
    Detect critical bottlenecks and blockers in the project.
    """
    try:
        project_oid = ObjectId(project_id)
        now = datetime.now()
        
        bottlenecks = {
            "critical_users": [],
            "long_overdue_tasks": [],
            "high_priority_blocked": [],
            "milestone_risks": []
        }
        
        # 1. CRITICAL USERS (overloaded with overdue tasks)
        active_tasks = list(db.tasks.find({
            "project_id": project_oid,
            "is_task_finished": False
        }))
        
        user_overdue = {}
        for task in active_tasks:
            if task.get("task_end_date") and task["task_end_date"] < now:
                for user_id in task.get("assigned_to", []):
                    user_id_str = str(user_id)
                    if user_id_str not in user_overdue:
                        user = db.users.find_one({"_id": user_id})
                        if user:
                            user_overdue[user_id_str] = {
                                "user_id": user_id_str,
                                "user_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                                "overdue_tasks": []
                            }
                    
                    if user_id_str in user_overdue:
                        days_overdue = (now - task["task_end_date"]).days
                        user_overdue[user_id_str]["overdue_tasks"].append({
                            "task_name": task.get("task_name"),
                            "days_overdue": days_overdue,
                            "priority": task.get("task_priority")
                        })
        
        # Users with 3+ overdue tasks are bottlenecks
        bottlenecks["critical_users"] = [
            {**user_data, "overdue_count": len(user_data["overdue_tasks"])}
            for user_data in user_overdue.values()
            if len(user_data["overdue_tasks"]) >= 3
        ]
        
        # 2. LONG OVERDUE TASKS (>14 days)
        long_overdue = [
            {
                "task_id": str(task["_id"]),
                "task_name": task.get("task_name"),
                "days_overdue": (now - task["task_end_date"]).days,
                "assigned_to": [
                    f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
                    for user_id in task.get("assigned_to", [])
                    if (u := db.users.find_one({"_id": user_id}))
                ],
                "priority": task.get("task_priority")
            }
            for task in active_tasks
            if task.get("task_end_date") and 
               (now - task["task_end_date"]).days > 14
        ]
        bottlenecks["long_overdue_tasks"] = sorted(long_overdue, key=lambda x: x["days_overdue"], reverse=True)
        
        # 3. HIGH PRIORITY BLOCKED TASKS
        high_priority_blocked = [
            {
                "task_id": str(task["_id"]),
                "task_name": task.get("task_name"),
                "priority": task.get("task_priority"),
                "status": task.get("status_name"),
                "assigned_to": [
                    f"{u.get('first_name', '')} {u.get('last_name', '')}".strip()
                    for user_id in task.get("assigned_to", [])
                    if (u := db.users.find_one({"_id": user_id}))
                ]
            }
            for task in active_tasks
            if task.get("task_priority") in ["High", "HIGH", "Critical", "CRITICAL"] and
               task.get("status_name") in ["BLOCKED", "Blocked", "On Hold"]
        ]
        bottlenecks["high_priority_blocked"] = high_priority_blocked
        
        # 4. MILESTONE RISKS
        milestones = list(db.milestones.find({"project_id": project_oid, "status": "1"}))
        
        for milestone in milestones:
            milestone_tasks = [t for t in active_tasks if t.get("milestone_id") == milestone["_id"]]
            
            if milestone_tasks:
                total = len(milestone_tasks)
                completed = sum(1 for t in milestone_tasks if t.get("is_task_finished", False))
                completion_pct = (completed / total * 100) if total > 0 else 0
                
                # Check if milestone end date is approaching
                if milestone.get("end_date"):
                    days_until = (milestone["end_date"] - now).days
                    
                    # Risk if <30% complete with <7 days left
                    if days_until <= 7 and completion_pct < 30:
                        bottlenecks["milestone_risks"].append({
                            "milestone_id": str(milestone["_id"]),
                            "milestone_title": milestone.get("title"),
                            "days_until_deadline": days_until,
                            "completion_percentage": round(completion_pct, 1),
                            "total_tasks": total,
                            "completed_tasks": completed,
                            "risk_level": "HIGH" if days_until <= 3 else "MEDIUM"
                        })
        
        # Calculate overall bottleneck severity
        severity_score = (
            len(bottlenecks["critical_users"]) * 3 +
            len(bottlenecks["long_overdue_tasks"]) * 2 +
            len(bottlenecks["high_priority_blocked"]) * 2 +
            len(bottlenecks["milestone_risks"]) * 4
        )
        
        if severity_score >= 15:
            severity = "CRITICAL"
        elif severity_score >= 8:
            severity = "HIGH"
        elif severity_score >= 3:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        return {
            "severity": severity,
            "severity_score": severity_score,
            "bottlenecks": bottlenecks,
            "summary": {
                "critical_users_count": len(bottlenecks["critical_users"]),
                "long_overdue_count": len(bottlenecks["long_overdue_tasks"]),
                "blocked_high_priority": len(bottlenecks["high_priority_blocked"]),
                "at_risk_milestones": len(bottlenecks["milestone_risks"])
            }
        }
        
    except Exception as e:
        import traceback
        return {
            "error": f"Bottleneck detection failed: {str(e)}",
            "traceback": traceback.format_exc()
        }


# ============================================================================
# MILESTONE RISK ANALYSIS
# ============================================================================

def analyze_milestone_risks(project_id: str) -> Dict[str, Any]:
    """
    Analyze completion risks for all active milestones.
    """
    try:
        project_oid = ObjectId(project_id)
        now = datetime.now()
        
        # Get all active milestones
        milestones = list(db.milestones.find({
            "project_id": project_oid,
            "status": "1"
        }))
        
        if not milestones:
            return {"message": "No active milestones found", "milestones": []}
        
        milestone_analysis = []
        
        for milestone in milestones:
            # Get tasks for this milestone
            tasks = list(db.tasks.find({"milestone_id": milestone["_id"]}))
            
            if not tasks:
                continue
            
            total_tasks = len(tasks)
            completed_tasks = sum(1 for t in tasks if t.get("is_task_finished", False))
            overdue_tasks = sum(
                1 for t in tasks
                if t.get("task_end_date") and
                   t["task_end_date"] < now and
                   not t.get("is_task_finished", False)
            )
            
            completion_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate risk
            risk_level = "LOW"
            risk_factors = []
            
            if milestone.get("end_date"):
                days_remaining = (milestone["end_date"] - now).days
                
                # Already overdue
                if days_remaining < 0:
                    risk_level = "CRITICAL"
                    risk_factors.append(f"Milestone is {abs(days_remaining)} days overdue")
                # Less than 7 days and not 80% complete
                elif days_remaining <= 7 and completion_pct < 80:
                    risk_level = "HIGH"
                    risk_factors.append(f"Only {days_remaining} days left with {completion_pct:.0f}% complete")
                # Less than 14 days and not 50% complete
                elif days_remaining <= 14 and completion_pct < 50:
                    risk_level = "MEDIUM"
                    risk_factors.append(f"{days_remaining} days left but only {completion_pct:.0f}% complete")
            
            # Overdue tasks factor
            if overdue_tasks > 0:
                overdue_pct = (overdue_tasks / total_tasks * 100)
                if overdue_pct > 30:
                    risk_level = "HIGH" if risk_level != "CRITICAL" else risk_level
                    risk_factors.append(f"{overdue_tasks} tasks overdue ({overdue_pct:.0f}%)")
            
            milestone_analysis.append({
                "milestone_id": str(milestone["_id"]),
                "milestone_title": milestone.get("title"),
                "start_date": milestone.get("start_date").strftime("%Y-%m-%d") if milestone.get("start_date") else None,
                "end_date": milestone.get("end_date").strftime("%Y-%m-%d") if milestone.get("end_date") else None,
                "days_remaining": (milestone["end_date"] - now).days if milestone.get("end_date") else None,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "completion_percentage": round(completion_pct, 1),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "in_progress_tasks": total_tasks - completed_tasks - overdue_tasks
            })
        
        # Sort by risk level
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        milestone_analysis.sort(key=lambda x: risk_order.get(x["risk_level"], 4))
        
        # Summary
        risk_counts = {
            "CRITICAL": sum(1 for m in milestone_analysis if m["risk_level"] == "CRITICAL"),
            "HIGH": sum(1 for m in milestone_analysis if m["risk_level"] == "HIGH"),
            "MEDIUM": sum(1 for m in milestone_analysis if m["risk_level"] == "MEDIUM"),
            "LOW": sum(1 for m in milestone_analysis if m["risk_level"] == "LOW")
        }
        
        return {
            "total_milestones": len(milestone_analysis),
            "risk_summary": risk_counts,
            "milestones": milestone_analysis
        }
        
    except Exception as e:
        import traceback
        return {
            "error": f"Milestone analysis failed: {str(e)}",
            "traceback": traceback.format_exc()
        }


# ============================================================================
# TEAM VELOCITY CALCULATION
# ============================================================================

def calculate_team_velocity(project_id: str, days: int = 7) -> Dict[str, Any]:
    """
    Calculate team velocity (tasks completed per day).
    """
    try:
        project_oid = ObjectId(project_id)
        
        # Get tasks completed in the time period
        cutoff_date = datetime.now() - timedelta(days=days)
        
        completed_tasks = list(db.tasks.find({
            "project_id": project_oid,
            "is_task_finished": True,
            "updatedAt": {"$gte": cutoff_date}
        }))
        
        # Get team size
        team_size = db.invite_users.count_documents({
            "project_id": project_oid,
            "status": "active"
        })
        
        tasks_completed = len(completed_tasks)
        velocity = tasks_completed / days if days > 0 else 0
        velocity_per_person = velocity / team_size if team_size > 0 else 0
        
        # Calculate trend by comparing first half vs second half
        midpoint = cutoff_date + timedelta(days=days/2)
        first_half = sum(1 for t in completed_tasks if t.get("updatedAt") < midpoint)
        second_half = tasks_completed - first_half
        
        if first_half > 0:
            trend_pct = ((second_half - first_half) / first_half) * 100
        else:
            trend_pct = 0
        
        if trend_pct > 20:
            trend = "ACCELERATING"
            trend_emoji = "📈"
        elif trend_pct < -20:
            trend = "SLOWING"
            trend_emoji = "📉"
        else:
            trend = "STEADY"
            trend_emoji = "➡️"
        
        return {
            "period_days": days,
            "tasks_completed": tasks_completed,
            "velocity_per_day": round(velocity, 2),
            "velocity_per_person_per_day": round(velocity_per_person, 2),
            "team_size": team_size,
            "trend": trend,
            "trend_emoji": trend_emoji,
            "trend_percentage": round(trend_pct, 1),
            "breakdown": {
                "first_half": first_half,
                "second_half": second_half
            }
        }
        
    except Exception as e:
        import traceback
        return {
            "error": f"Velocity calculation failed: {str(e)}",
            "traceback": traceback.format_exc()
        }