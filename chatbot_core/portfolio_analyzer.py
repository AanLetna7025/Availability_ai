# chatbot_core/portfolio_analyzer.py

"""
Portfolio-wide analysis across all projects
Aggregates insights and generates AI-powered recommendations
"""

import os
import re
import json
from typing import Dict, List, Any
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from .analysis_tool import (
    calculate_project_health,
    analyze_team_workload_balance,
    detect_bottlenecks,
    analyze_milestone_risks,
    calculate_team_velocity
)
from .tools import db

load_dotenv()

# ============================================================================
# PORTFOLIO DATA AGGREGATION
# ============================================================================

def get_all_projects() -> List[Dict[str, Any]]:
    """
    Fetch all active projects from MongoDB.
    """
    try:
        projects = list(db.projects.find(
            {"status": {"$in": ["ongoing", "active", "in_progress"]}},
            {
                "_id": 1,
                "name": 1,
                "description": 1,
                "start_date": 1,
                "end_date": 1,
                "status": 1,
                "client": 1
            }
        ))
        
        # Convert ObjectIds to strings
        for project in projects:
            project['_id'] = str(project['_id'])
            project['project_id'] = project['_id']
            if project.get('client'):
                # Get client name
                client = db.clients.find_one({"_id": project['client']})
                project['client_name'] = client.get('name', 'Unknown') if client else 'Unknown'
            else:
                project['client_name'] = 'No Client'
        
        return projects
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []


def analyze_portfolio() -> Dict[str, Any]:
    """
    Analyze all projects and aggregate portfolio-level insights.
    """
    projects = get_all_projects()
    
    if not projects:
        return {
            "error": "No active projects found",
            "total_projects": 0,
            "portfolio_health": 0
        }
    
    portfolio_data = {
        "total_projects": len(projects),
        "timestamp": datetime.now().isoformat(),
        "projects": [],
        "aggregated_metrics": {
            "total_tasks": 0,
            "total_completed": 0,
            "total_overdue": 0,
            "total_team_members": 0,
            "avg_completion_rate": 0,
            "critical_projects": 0,
            "at_risk_projects": 0,
            "healthy_projects": 0
        },
        "critical_alerts": [],
        "resource_insights": {
            "overloaded_members": [],
            "cross_project_bottlenecks": []
        }
    }
    
    health_scores = []
    all_team_members = set()
    user_project_count = {}  # Track how many projects each user is in
    
    # Analyze each project
    for project in projects:
        project_id = project['_id']
        
        try:
            # Get comprehensive analysis
            health = calculate_project_health(project_id)
            workload = analyze_team_workload_balance(project_id)
            bottlenecks = detect_bottlenecks(project_id)
            milestones = analyze_milestone_risks(project_id)
            velocity = calculate_team_velocity(project_id, days=7)
            
            # Skip if health analysis failed
            if "error" in health:
                continue
            
            # Build project summary
            project_summary = {
                "project_id": project_id,
                "project_name": project.get('name', 'Unnamed Project'),
                "client": project.get('client_name', 'No Client'),
                "health_score": health.get('health_score', 0),
                "health_status": health.get('health_status', 'UNKNOWN'),
                "status_emoji": health.get('status_emoji', '⚪'),
                "metrics": health.get('metrics', {}),
                "completion_rate": health.get('metrics', {}).get('completion_rate', 0),
                "overdue_tasks": health.get('metrics', {}).get('overdue_tasks', 0),
                "team_size": health.get('metrics', {}).get('team_size', 0),
                "velocity": velocity.get('velocity_per_day', 0),
                "velocity_trend": velocity.get('trend', 'UNKNOWN'),
                "critical_issues": []
            }
            
            # Track health distribution
            health_scores.append(health.get('health_score', 0))
            status = health.get('health_status', 'UNKNOWN')
            
            if status == 'CRITICAL':
                portfolio_data['aggregated_metrics']['critical_projects'] += 1
            elif status in ['AT_RISK', 'GOOD']:
                portfolio_data['aggregated_metrics']['at_risk_projects'] += 1
            else:
                portfolio_data['aggregated_metrics']['healthy_projects'] += 1
            
            # Aggregate metrics
            metrics = health.get('metrics', {})
            portfolio_data['aggregated_metrics']['total_tasks'] += metrics.get('total_tasks', 0)
            portfolio_data['aggregated_metrics']['total_completed'] += metrics.get('completed_tasks', 0)
            portfolio_data['aggregated_metrics']['total_overdue'] += metrics.get('overdue_tasks', 0)
            portfolio_data['aggregated_metrics']['total_team_members'] += metrics.get('team_size', 0)
            
            # Identify critical issues
            if health.get('health_score', 0) < 50:
                project_summary['critical_issues'].append(f"Health score critically low: {health.get('health_score', 0)}/100")
            
            if metrics.get('overdue_tasks', 0) > 5:
                project_summary['critical_issues'].append(f"{metrics.get('overdue_tasks', 0)} tasks overdue")
            
            # Check for bottlenecks
            if bottlenecks.get('severity') in ['CRITICAL', 'HIGH']:
                project_summary['critical_issues'].append(f"Bottleneck severity: {bottlenecks.get('severity')}")
            
            # Check milestone risks
            at_risk_milestones = [
                m for m in milestones.get('milestones', [])
                if m.get('risk_level') in ['CRITICAL', 'HIGH']
            ]
            if at_risk_milestones:
                project_summary['critical_issues'].append(f"{len(at_risk_milestones)} milestones at risk")
            
            # Track team members across projects
            if "error" not in workload:
                for member in workload.get('all_members', []):
                    user_id = member['user_id']
                    all_team_members.add(user_id)
                    
                    if user_id not in user_project_count:
                        user_project_count[user_id] = {
                            "name": member['user_name'],
                            "projects": [],
                            "total_tasks": 0,
                            "overdue_tasks": 0
                        }
                    
                    user_project_count[user_id]['projects'].append(project.get('name', 'Unnamed'))
                    user_project_count[user_id]['total_tasks'] += member['total_tasks']
                    user_project_count[user_id]['overdue_tasks'] += member['overdue_tasks']
            
            portfolio_data['projects'].append(project_summary)
            
        except Exception as e:
            print(f"Error analyzing project {project_id}: {e}")
            continue
    
    # Calculate portfolio-wide metrics
    if health_scores:
        portfolio_data['portfolio_health'] = round(sum(health_scores) / len(health_scores))
    else:
        portfolio_data['portfolio_health'] = 0
    
    if portfolio_data['aggregated_metrics']['total_tasks'] > 0:
        completion_rate = (
            portfolio_data['aggregated_metrics']['total_completed'] /
            portfolio_data['aggregated_metrics']['total_tasks'] * 100
        )
        portfolio_data['aggregated_metrics']['avg_completion_rate'] = round(completion_rate, 1)
    
    # Identify cross-project resource issues
    for user_id, user_data in user_project_count.items():
        project_count = len(user_data['projects'])
        
        # Overloaded: Working on 3+ projects with 10+ tasks total
        if project_count >= 3 and user_data['total_tasks'] >= 10:
            portfolio_data['resource_insights']['overloaded_members'].append({
                "name": user_data['name'],
                "project_count": project_count,
                "projects": user_data['projects'],
                "total_tasks": user_data['total_tasks'],
                "overdue_tasks": user_data['overdue_tasks']
            })
    
    # Generate critical alerts
    if portfolio_data['aggregated_metrics']['critical_projects'] > 0:
        portfolio_data['critical_alerts'].append({
            "severity": "HIGH",
            "message": f"{portfolio_data['aggregated_metrics']['critical_projects']} project(s) in critical state",
            "category": "PROJECT_HEALTH"
        })
    
    if portfolio_data['aggregated_metrics']['total_overdue'] > 20:
        portfolio_data['critical_alerts'].append({
            "severity": "HIGH",
            "message": f"{portfolio_data['aggregated_metrics']['total_overdue']} overdue tasks across portfolio",
            "category": "TIMELINE"
        })
    
    if len(portfolio_data['resource_insights']['overloaded_members']) > 0:
        portfolio_data['critical_alerts'].append({
            "severity": "MEDIUM",
            "message": f"{len(portfolio_data['resource_insights']['overloaded_members'])} team member(s) overloaded across multiple projects",
            "category": "RESOURCES"
        })
    
    # Sort projects by health score (worst first)
    portfolio_data['projects'].sort(key=lambda x: x['health_score'])
    
    return portfolio_data


# ============================================================================
# AI-POWERED PORTFOLIO INSIGHTS
# ============================================================================

def generate_portfolio_insights(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use AI to generate executive insights about the entire portfolio.
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
            temperature=0.2,  # slightly lower for more consistent JSON
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

        agg = portfolio_data.get("aggregated_metrics", {}) or {}
        res = portfolio_data.get("resource_insights", {}) or {}
        projects = portfolio_data.get("projects", []) or []

        total_projects = portfolio_data.get("total_projects", 0)
        portfolio_health = portfolio_data.get("portfolio_health", 0)

        # ---------------- Context building ----------------
        context = f"""You are a senior portfolio manager analyzing {total_projects} software projects.

PORTFOLIO OVERVIEW:
- Total Projects: {total_projects}
- Portfolio Health: {portfolio_health}/100
- Total Tasks: {agg.get('total_tasks', 0)}
- Completion Rate: {agg.get('avg_completion_rate', 0)}%
- Overdue Tasks: {agg.get('total_overdue', 0)}
- Total Team Members: {agg.get('total_team_members', 0)}

PROJECT STATUS DISTRIBUTION:
- Critical: {agg.get('critical_projects', 0)}
- At Risk: {agg.get('at_risk_projects', 0)}
- Healthy: {agg.get('healthy_projects', 0)}

TOP 5 PROJECTS NEEDING ATTENTION:
"""

        for i, project in enumerate(projects[:5], 1):
            name = project.get("project_name", "Unnamed Project")
            health_score = project.get("health_score", 0)
            health_status = project.get("health_status", "UNKNOWN")
            completion_rate = project.get("completion_rate", 0)
            overdue_tasks = project.get("overdue_tasks", 0)
            critical_issues = project.get("critical_issues", []) or []

            context += f"\n{i}. {name} (Health: {health_score}/100)\n"
            context += f"   - Status: {health_status}\n"
            context += f"   - Completion: {completion_rate}%\n"
            context += f"   - Overdue: {overdue_tasks} tasks\n"
            if critical_issues:
                context += f"   - Issues: {', '.join(critical_issues[:2])}\n"

        overloaded_members = res.get("overloaded_members", []) or []
        if overloaded_members:
            context += "\nCROSS-PROJECT RESOURCE ISSUES:\n"
            for member in overloaded_members[:3]:
                name = member.get("name", "Unknown")
                project_count = member.get("project_count", 0)
                total_tasks = member.get("total_tasks", 0)
                context += f"- {name}: Working on {project_count} projects ({total_tasks} tasks)\n"

        # ---------------- Prompt instructions ----------------
        context += """
Generate an executive summary in JSON format ONLY.

REQUIREMENTS:
- Output MUST be a single valid JSON object.
- Do NOT include markdown, code fences, comments, or any surrounding text.
- Use a concise, professional, executive tone.
- Use specific numbers and project names from the data above.
- Focus on:
  1. Specific numbers and project names
  2. Actionable insights (not vague advice)
  3. Resource allocation opportunities
  4. Risk mitigation priorities

The JSON object MUST follow this structure (these are examples, not literal text):

{
  "executive_summary": "2-3 sentence overview of portfolio health, key risks and opportunities.",
  "key_insights": [
    "Insight 1: Specific observation with data.",
    "Insight 2: Pattern or trend identified with metrics.",
    "Insight 3: Resource or bottleneck issue referencing overloaded members or critical projects."
  ],
  "immediate_actions": [
    "Action 1: Specific, actionable recommendation with clear next step.",
    "Action 2: Resource reallocation suggestion referencing projects/teams.",
    "Action 3: Risk mitigation step with concrete focus."
  ],
  "positive_trends": [
    "Positive trend 1 with numbers.",
    "Positive trend 2 highlighting strong performance."
  ]
}

Now respond with ONLY the JSON object, and nothing else.
"""

        # ---------------- LLM call ----------------
        response = llm.invoke(context)
        response_text = getattr(response, "content", response)
        if not isinstance(response_text, str):
            response_text = str(response_text)

        # ---------------- JSON parsing strategy ----------------
        insights = None

        # 1) Try raw JSON
        try:
            insights = json.loads(response_text)
        except json.JSONDecodeError:
            # 2) Try to extract first {...} block
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                try:
                    insights = json.loads(match.group(0))
                except json.JSONDecodeError:
                    insights = None

        if isinstance(insights, dict):
            return {
                "success": True,
                "insights": insights,
                "generated_at": datetime.now().isoformat(),
                "method": "ai",
            }

    
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        

#         # If parsing fails, use rules
#         return generate_rule_based_portfolio_insights(portfolio_data)

#     except Exception as e:
#         print(f"Error generating AI insights: {e}")
#         return generate_rule_based_portfolio_insights(portfolio_data)


# def generate_rule_based_portfolio_insights(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Fallback: Generate portfolio insights using rules (no AI).
#     Keeps your original logic but adds safe access and slightly more
#     polished wording.
#     """
#     agg = portfolio_data.get("aggregated_metrics", {}) or {}
#     res = portfolio_data.get("resource_insights", {}) or {}
#     projects = portfolio_data.get("projects", []) or []

#     health = portfolio_data.get("portfolio_health", 0)
#     critical = agg.get("critical_projects", 0)
#     overdue = agg.get("total_overdue", 0)
#     healthy = agg.get("healthy_projects", 0)
#     completion_rate = agg.get("avg_completion_rate", 0)
#     overloaded_members = res.get("overloaded_members", []) or []
#     overloaded_count = len(overloaded_members)

#     insights = {
#         "executive_summary": "",
#         "key_insights": [],
#         "immediate_actions": [],
#         "positive_trends": [],
#     }

#     # Executive summary
#     if health >= 70:
#         insights["executive_summary"] = (
#             f"Portfolio is performing well with an average health score of {health}/100. "
#         )
#     elif health >= 50:
#         insights["executive_summary"] = (
#             f"Portfolio shows moderate health ({health}/100) with some areas requiring attention. "
#         )
#     else:
#         insights["executive_summary"] = (
#             f"Portfolio requires immediate attention with a health score of {health}/100. "
#         )

#     if critical > 0:
#         insights["executive_summary"] += f"{critical} project(s) are in a critical state."

#     # Key insights
#     if overdue > 20:
#         insights["key_insights"].append(
#             f"High volume of overdue work: {overdue} task(s) remain open across the portfolio."
#         )

#     if critical > 0 and projects:
#         worst_projects = projects[:3]
#         names = ", ".join([p.get("project_name", "Unnamed Project") for p in worst_projects])
#         insights["key_insights"].append(
#             f"Critical projects requiring immediate attention: {names}."
#         )

#     if overloaded_count > 0:
#         insights["key_insights"].append(
#             f"{overloaded_count} team member(s) are working across 3 or more projects, indicating potential overload."
#         )

#     # Immediate actions
#     if critical > 0:
#         insights["immediate_actions"].append(
#             f"Conduct an urgent review of the {critical} critical project(s) and define clear recovery plans."
#         )

#     if overdue > 10:
#         insights["immediate_actions"].append(
#             "Plan a focused sprint to reduce the overdue task backlog in the most impacted projects."
#         )

#     if overloaded_count > 0:
#         insights["immediate_actions"].append(
#             "Rebalance workload for overloaded team members by shifting tasks to available capacity."
#         )

#     # Positive trends
#     if healthy > 0:
#         insights["positive_trends"].append(
#             f"{healthy} project(s) are maintaining strong health, providing stability to the portfolio."
#         )

#     if completion_rate > 60:
#         insights["positive_trends"].append(
#             f"Overall completion rate is solid at {completion_rate}%, indicating steady delivery."
#         )

#     return {
#         "success": True,
#         "insights": insights,
#         "generated_at": datetime.now().isoformat(),
#         "method": "rules",
#     }