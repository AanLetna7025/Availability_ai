# chatbot_core/recommendation_engine.py

"""
Generate actionable recommendations to improve project health
"""

import os
import time
import traceback
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

def generate_ai_recommendations(project_id: str, max_recommendations: int = 5, max_retries: int = 2) -> Dict[str, Any]:
    """
    Use AI (Gemini) to generate intelligent, context-aware recommendations.
    Includes retry logic for reliability.
    """
    for attempt in range(max_retries):
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
                temperature=0.3,
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
            
            # Try to parse
            result = json.loads(response_text)
            
            # Validate structure
            if "recommendations" not in result or not isinstance(result["recommendations"], list):
                raise ValueError("Invalid response structure - missing recommendations array")
            
            # Limit to max_recommendations
            result["recommendations"] = result["recommendations"][:max_recommendations]
            
            return {
                "method": "ai",
                "recommendations": result["recommendations"],
                "total": len(result["recommendations"]),
                "success": True
            }
            
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"[RETRY {attempt + 1}] JSON parsing failed, retrying...")
                continue
            else:
                return {
                    "error": f"AI failed to generate valid JSON after {max_retries} attempts: {str(e)}",
                    "traceback": traceback.format_exc(),
                    "recommendations": [],
                    "total": 0,
                    "method": "ai",
                    "success": False
                }
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[RETRY {attempt + 1}] AI generation failed, retrying...")
                time.sleep(1)  # Brief pause before retry
                continue
            else:
                return {
                    "error": f"AI recommendation generation failed after {max_retries} attempts: {str(e)}",
                    "traceback": traceback.format_exc(),
                    "recommendations": [],
                    "total": 0,
                    "method": "ai",
                    "success": False
                }