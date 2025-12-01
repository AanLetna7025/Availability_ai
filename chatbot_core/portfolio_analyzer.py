# chatbot_core/portfolio_analyzer.py

"""
Portfolio-wide analysis across all projects
Aggregates insights and generates AI-powered recommendations
"""

import os
from typing import Dict, List, Any
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
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
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Build context for AI
        context = f"""You are a senior portfolio manager analyzing {portfolio_data['total_projects']} software projects.

PORTFOLIO OVERVIEW:
- Total Projects: {portfolio_data['total_projects']}
- Portfolio Health: {portfolio_data['portfolio_health']}/100
- Total Tasks: {portfolio_data['aggregated_metrics']['total_tasks']}
- Completion Rate: {portfolio_data['aggregated_metrics']['avg_completion_rate']}%
- Overdue Tasks: {portfolio_data['aggregated_metrics']['total_overdue']}
- Total Team Members: {portfolio_data['aggregated_metrics']['total_team_members']}

PROJECT STATUS DISTRIBUTION:
- Critical: {portfolio_data['aggregated_metrics']['critical_projects']}
- At Risk: {portfolio_data['aggregated_metrics']['at_risk_projects']}
- Healthy: {portfolio_data['aggregated_metrics']['healthy_projects']}

TOP 5 PROJECTS NEEDING ATTENTION:
"""
        
        # Add details of worst-performing projects
        for i, project in enumerate(portfolio_data['projects'][:5], 1):
            context += f"\n{i}. {project['project_name']} (Health: {project['health_score']}/100)\n"
            context += f"   - Status: {project['health_status']}\n"
            context += f"   - Completion: {project['completion_rate']}%\n"
            context += f"   - Overdue: {project['overdue_tasks']} tasks\n"
            if project['critical_issues']:
                context += f"   - Issues: {', '.join(project['critical_issues'][:2])}\n"
        
        # Add resource insights
        if portfolio_data['resource_insights']['overloaded_members']:
            context += "\nCROSS-PROJECT RESOURCE ISSUES:\n"
            for member in portfolio_data['resource_insights']['overloaded_members'][:3]:
                context += f"- {member['name']}: Working on {member['project_count']} projects ({member['total_tasks']} tasks)\n"
        
        context += """

Generate an executive summary in JSON format:
{
    "executive_summary": "2-3 sentence overview of portfolio health",
    "key_insights": [
        "Insight 1: Specific observation with data",
        "Insight 2: Pattern or trend identified",
        "Insight 3: Resource or bottleneck issue"
    ],
    "immediate_actions": [
        "Action 1: Specific, actionable recommendation",
        "Action 2: Resource reallocation suggestion",
        "Action 3: Risk mitigation step"
    ],
    "positive_trends": [
        "Positive trend 1",
        "Positive trend 2"
    ]
}

Focus on:
1. Specific numbers and project names
2. Actionable insights (not vague advice)
3. Resource allocation opportunities
4. Risk mitigation priorities
"""
        
        response = llm.invoke(context)
        
        # Parse JSON response
        import json
        import re
        
        response_text = response.content
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        try:
            insights = json.loads(response_text)
            return {
                "success": True,
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
        except json.JSONDecodeError:
            # Fallback to rule-based insights
            return generate_rule_based_portfolio_insights(portfolio_data)
        
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return generate_rule_based_portfolio_insights(portfolio_data)


def generate_rule_based_portfolio_insights(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback: Generate portfolio insights using rules (no AI).
    """
    insights = {
        "executive_summary": "",
        "key_insights": [],
        "immediate_actions": [],
        "positive_trends": []
    }
    
    # Executive summary
    health = portfolio_data['portfolio_health']
    critical = portfolio_data['aggregated_metrics']['critical_projects']
    
    if health >= 70:
        insights['executive_summary'] = f"Portfolio is performing well with an average health score of {health}/100. "
    elif health >= 50:
        insights['executive_summary'] = f"Portfolio shows moderate health ({health}/100) with some areas requiring attention. "
    else:
        insights['executive_summary'] = f"Portfolio requires immediate attention with health score of {health}/100. "
    
    if critical > 0:
        insights['executive_summary'] += f"{critical} project(s) are in critical state."
    
    # Key insights
    overdue = portfolio_data['aggregated_metrics']['total_overdue']
    if overdue > 20:
        insights['key_insights'].append(f"High volume of overdue tasks: {overdue} tasks across portfolio")
    
    if critical > 0:
        worst_projects = portfolio_data['projects'][:3]
        project_names = ', '.join([p['project_name'] for p in worst_projects])
        insights['key_insights'].append(f"Critical projects requiring attention: {project_names}")
    
    overloaded = len(portfolio_data['resource_insights']['overloaded_members'])
    if overloaded > 0:
        insights['key_insights'].append(f"{overloaded} team member(s) working across 3+ projects simultaneously")
    
    # Immediate actions
    if critical > 0:
        insights['immediate_actions'].append(f"Conduct emergency review of {critical} critical project(s)")
    
    if overdue > 10:
        insights['immediate_actions'].append("Organize sprint to clear overdue task backlog")
    
    if overloaded > 0:
        insights['immediate_actions'].append("Reassess resource allocation across projects")
    
    # Positive trends
    healthy = portfolio_data['aggregated_metrics']['healthy_projects']
    if healthy > 0:
        insights['positive_trends'].append(f"{healthy} project(s) maintaining excellent health")
    
    completion_rate = portfolio_data['aggregated_metrics']['avg_completion_rate']
    if completion_rate > 60:
        insights['positive_trends'].append(f"Strong completion rate: {completion_rate}%")
    
    return {
        "success": True,
        "insights": insights,
        "generated_at": datetime.now().isoformat(),
        "method": "rules"
    }