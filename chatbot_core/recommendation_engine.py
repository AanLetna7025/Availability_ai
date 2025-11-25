# chatbot_core/recommendation_engine.py

"""
Generate actionable recommendations to improve project health
"""

import os
from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from .analysis_tool import (
    calculate_project_health,
    analyze_team_workload_balance,
    detect_bottlenecks,
    analyze_milestone_risks,
    calculate_team_velocity
)

load_dotenv()

# ============================================================================
# AI-POWERED RECOMMENDATIONS
# ============================================================================

def generate_ai_recommendations(project_id: str, max_recommendations: int = 5) -> Dict[str, Any]:
    """
    Use AI (Gemini) to generate intelligent, context-aware recommendations.
    """
    try:
        # Gather comprehensive project data
        health = calculate_project_health(project_id)
        workload = analyze_team_workload_balance(project_id)
        bottlenecks = detect_bottlenecks(project_id)
        milestones = analyze_milestone_risks(project_id)
        velocity = calculate_team_velocity(project_id, days=7)
        
        # Build comprehensive context for AI
        context = f"""
You are a senior project manager analyzing a software development project.

PROJECT HEALTH:
- Overall Score: {health.get('health_score', 0)}/100
- Status: {health.get('health_status', 'UNKNOWN')}
- Completion Rate: {health.get('metrics', {}).get('completion_rate', 0)}%
- Overdue Tasks: {health.get('metrics', {}).get('overdue_tasks', 0)}
- Team Size: {health.get('metrics', {}).get('team_size', 0)}

TEAM WORKLOAD:
- Balance Status: {workload.get('balance_status', 'UNKNOWN')}
- Average Tasks/Person: {workload.get('statistics', {}).get('average_tasks_per_person', 0)}
- Overloaded Members: {workload.get('categories', {}).get('overloaded_count', 0)}
- Underutilized Members: {workload.get('categories', {}).get('underutilized_count', 0)}

"""
        
        # Add overloaded members details
        if workload.get('overloaded_members'):
            context += "OVERLOADED TEAM MEMBERS:\n"
            for member in workload['overloaded_members'][:3]:
                context += f"- {member['user_name']}: {member['total_tasks']} tasks ({member['overdue_tasks']} overdue)\n"
            context += "\n"
        
        # Add underutilized members
        if workload.get('underutilized_members'):
            context += "AVAILABLE/UNDERUTILIZED MEMBERS:\n"
            for member in workload['underutilized_members'][:3]:
                context += f"- {member['user_name']}: {member['total_tasks']} tasks\n"
            context += "\n"
        
        context += f"""
BOTTLENECKS (Severity: {bottlenecks.get('severity', 'UNKNOWN')}):
- Critical Users: {bottlenecks.get('summary', {}).get('critical_users_count', 0)}
- Long Overdue Tasks: {bottlenecks.get('summary', {}).get('long_overdue_count', 0)}
- Blocked High Priority: {bottlenecks.get('summary', {}).get('blocked_high_priority', 0)}

"""
        
        # Add milestone risks
        if milestones.get('milestones'):
            at_risk = [m for m in milestones['milestones'] if m['risk_level'] in ['CRITICAL', 'HIGH']]
            if at_risk:
                context += "AT-RISK MILESTONES:\n"
                for m in at_risk[:3]:
                    context += f"- {m['milestone_title']}: {m['completion_percentage']}% complete, {m.get('days_remaining', 'N/A')} days left\n"
                context += "\n"
        
        context += f"""
TEAM VELOCITY:
- Tasks Completed (7 days): {velocity.get('tasks_completed', 0)}
- Trend: {velocity.get('trend', 'UNKNOWN')}

Based on this data, generate {max_recommendations} specific, actionable recommendations to improve project health.

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "recommendations": [
        {{
            "priority": "HIGH" | "MEDIUM" | "LOW",
            "category": "WORKLOAD" | "TIMELINE" | "QUALITY" | "TEAM" | "PROCESS",
            "action": "Specific action to take (be detailed)",
            "reason": "Why this is important",
            "expected_impact": "What improvement this will bring",
            "effort": "LOW" | "MEDIUM" | "HIGH"
        }}
    ]
}}

RULES:
1. Be SPECIFIC: Mention actual user names, task counts, numbers
2. Be ACTIONABLE: Clear actions that can be done immediately
3. Prioritize HIGH for urgent issues affecting delivery
4. Focus on quick wins (LOW effort, HIGH impact) when possible
5. Consider both immediate fixes and long-term improvements
"""
        
        # Call Gemini
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
            temperature=0.3,  # Some creativity but mostly focused
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        response = llm.invoke(context)
        
        # Parse JSON response
        import json
        import re
        
        response_text = response.content
        
        # Extract JSON from markdown if present
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        try:
            result = json.loads(response_text)
            
            # Validate structure
            if "recommendations" not in result or not isinstance(result["recommendations"], list):
                raise ValueError("Invalid response structure")
            
            # Limit to max_recommendations
            result["recommendations"] = result["recommendations"][:max_recommendations]
            
            return {
                "method": "ai",
                "recommendations": result["recommendations"],
                "total": len(result["recommendations"])
            }
            
        except json.JSONDecodeError as e:
            # Fallback to rule-based if JSON parsing fails
            print(f"AI response parsing failed: {e}. Falling back to rule-based.")
            return generate_rule_based_recommendations(project_id)
        
    except Exception as e:
        import traceback
        return {
            "error": f"AI recommendation generation failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "fallback": "Use /recommendations/rules endpoint for rule-based recommendations"
        }


# ============================================================================
# RULE-BASED RECOMMENDATIONS (Deterministic Fallback)
# ============================================================================

def generate_rule_based_recommendations(project_id: str) -> Dict[str, Any]:
    """
    Generate recommendations using deterministic rules.
    Fast and reliable fallback when AI is unavailable.
    """
    try:
        # Gather data
        health = calculate_project_health(project_id)
        workload = analyze_team_workload_balance(project_id)
        bottlenecks = detect_bottlenecks(project_id)
        milestones = analyze_milestone_risks(project_id)
        velocity = calculate_team_velocity(project_id, days=7)
        
        recommendations = []
        
        # RULE 1: Critical Health Score
        if health.get('health_score', 0) < 40:
            recommendations.append({
                "priority": "HIGH",
                "category": "TIMELINE",
                "action": f"Schedule emergency project review meeting to address critical health score of {health.get('health_score', 0)}/100",
                "reason": "Project health is in critical state with multiple compounding issues",
                "expected_impact": "Identify root causes and create recovery plan",
                "effort": "LOW"
            })
        
        # RULE 2: Overdue Tasks
        overdue_count = health.get('metrics', {}).get('overdue_tasks', 0)
        if overdue_count > 5:
            recommendations.append({
                "priority": "HIGH",
                "category": "TIMELINE",
                "action": f"Organize overdue task sprint: prioritize and complete {overdue_count} overdue tasks",
                "reason": f"High number of overdue tasks ({overdue_count}) is blocking project progress",
                "expected_impact": "Clear backlog and improve timeline score by ~15-20 points",
                "effort": "MEDIUM"
            })
        elif overdue_count > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "TIMELINE",
                "action": f"Address {overdue_count} overdue task(s) this week",
                "reason": "Prevent overdue tasks from accumulating",
                "expected_impact": "Maintain timeline adherence",
                "effort": "LOW"
            })
        
        # RULE 3: Overloaded Team Members
        overloaded = workload.get('overloaded_members', [])
        underutilized = workload.get('underutilized_members', [])
        
        if overloaded and underutilized:
            # Specific reassignment recommendations
            from_member = overloaded[0]
            to_member = underutilized[0]
            
            tasks_to_move = max(2, int(from_member['total_tasks'] * 0.25))  # Move 25% of tasks
            
            recommendations.append({
                "priority": "HIGH",
                "category": "WORKLOAD",
                "action": f"Reassign {tasks_to_move} tasks from {from_member['user_name']} to {to_member['user_name']}",
                "reason": f"{from_member['user_name']} has {from_member['total_tasks']} tasks ({from_member['overdue_tasks']} overdue), while {to_member['user_name']} has only {to_member['total_tasks']}",
                "expected_impact": "Balance workload and improve completion rate by ~10-15%",
                "effort": "LOW"
            })
        elif overloaded:
            recommendations.append({
                "priority": "HIGH",
                "category": "WORKLOAD",
                "action": f"Reduce workload for {len(overloaded)} overloaded team member(s): {', '.join([m['user_name'] for m in overloaded[:3]])}",
                "reason": "Overloaded members are bottlenecks for project progress",
                "expected_impact": "Improve task completion velocity",
                "effort": "MEDIUM"
            })
        
        # RULE 4: At-Risk Milestones
        at_risk_milestones = [m for m in milestones.get('milestones', []) if m['risk_level'] in ['CRITICAL', 'HIGH']]
        
        if at_risk_milestones:
            milestone = at_risk_milestones[0]  # Most at risk
            
            if milestone.get('days_remaining', 100) < 0:
                action = f"URGENT: Milestone '{milestone['milestone_title']}' is overdue. Assess extension or scope reduction"
            elif milestone['completion_percentage'] < 50:
                action = f"Prioritize tasks for milestone '{milestone['milestone_title']}' - currently only {milestone['completion_percentage']}% complete"
            else:
                action = f"Add resources to milestone '{milestone['milestone_title']}' to ensure on-time delivery"
            
            recommendations.append({
                "priority": "HIGH",
                "category": "TIMELINE",
                "action": action,
                "reason": f"Milestone has {milestone.get('days_remaining', 'unknown')} days left with {milestone['overdue_tasks']} overdue tasks",
                "expected_impact": "Protect milestone deadline and deliverables",
                "effort": "MEDIUM"
            })
        
        # RULE 5: Low Velocity
        if velocity.get('trend') == 'SLOWING':
            recommendations.append({
                "priority": "MEDIUM",
                "category": "PROCESS",
                "action": "Investigate velocity slowdown: check for blockers, resource constraints, or process issues",
                "reason": f"Team velocity has decreased by {abs(velocity.get('trend_percentage', 0))}%",
                "expected_impact": "Identify and remove impediments to team productivity",
                "effort": "LOW"
            })
        
        # RULE 6: Critical Users (Bottlenecks)
        critical_users = bottlenecks.get('bottlenecks', {}).get('critical_users', [])
        if critical_users:
            user = critical_users[0]
            recommendations.append({
                "priority": "HIGH",
                "category": "TEAM",
                "action": f"Provide support to {user['user_name']} who has {user['overdue_count']} overdue tasks",
                "reason": "This team member is a critical bottleneck blocking project progress",
                "expected_impact": "Unblock dependencies and improve flow",
                "effort": "LOW"
            })
        
        # RULE 7: Long Overdue Tasks
        long_overdue = bottlenecks.get('bottlenecks', {}).get('long_overdue_tasks', [])
        if long_overdue:
            task = long_overdue[0]
            recommendations.append({
                "priority": "HIGH",
                "category": "QUALITY",
                "action": f"Review task '{task['task_name']}' which is {task['days_overdue']} days overdue - consider closing or reassigning",
                "reason": "Extremely overdue tasks often indicate stale work or blocked progress",
                "expected_impact": "Clean up backlog and clarify project status",
                "effort": "LOW"
            })
        
        # RULE 8: Blocked High Priority Tasks
        blocked_tasks = bottlenecks.get('bottlenecks', {}).get('high_priority_blocked', [])
        if blocked_tasks:
            recommendations.append({
                "priority": "HIGH",
                "category": "QUALITY",
                "action": f"Unblock {len(blocked_tasks)} high-priority task(s) that are currently blocked",
                "reason": "High-priority work is stalled, impacting deliverables",
                "expected_impact": "Resume progress on critical features",
                "effort": "MEDIUM"
            })
        
        # RULE 9: Good Health - Maintain Momentum
        if health.get('health_score', 0) >= 80 and not recommendations:
            recommendations.append({
                "priority": "LOW",
                "category": "PROCESS",
                "action": "Maintain current trajectory - project is performing well",
                "reason": f"Health score is {health.get('health_score', 0)}/100 with no critical issues",
                "expected_impact": "Continue steady progress toward goals",
                "effort": "LOW"
            })
        
        # RULE 10: Low Completion Rate
        completion_rate = health.get('metrics', {}).get('completion_rate', 0)
        if completion_rate < 30 and len(recommendations) < 3:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "TIMELINE",
                "action": f"Focus on completing in-progress tasks - only {completion_rate}% done",
                "reason": "Low completion rate suggests too much WIP or scope creep",
                "expected_impact": "Improve completion rate and demonstrate progress",
                "effort": "MEDIUM"
            })
        
        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        # Limit to top 5-7 recommendations
        recommendations = recommendations[:7]
        
        return {
            "method": "rules",
            "recommendations": recommendations,
            "total": len(recommendations)
        }
        
    except Exception as e:
        import traceback
        return {
            "error": f"Rule-based recommendation generation failed: {str(e)}",
            "traceback": traceback.format_exc()
        }