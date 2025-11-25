# chatbot_core/report_generator.py

"""
Generate formatted reports for projects
"""

from datetime import datetime
from typing import Dict, Any
from .analysis_tool import (
    calculate_project_health,
    analyze_team_workload_balance,
    detect_bottlenecks,
    analyze_milestone_risks,
    calculate_team_velocity
)

# ============================================================================
# DAILY REPORT
# ============================================================================

def generate_daily_report(project_id: str) -> str:
    """
    Generate a concise daily status report.
    """
    try:
        # Gather all data
        health = calculate_project_health(project_id)
        workload = analyze_team_workload_balance(project_id)
        velocity = calculate_team_velocity(project_id, days=1)
        bottlenecks = detect_bottlenecks(project_id)
        
        # Build report
        report = f"""
{'='*70}
📊 DAILY PROJECT STATUS REPORT
{'='*70}
Project: {health.get('project_name', 'Unknown')}
Date: {datetime.now().strftime('%A, %B %d, %Y')}
Generated at: {datetime.now().strftime('%I:%M %p')}

{'─'*70}
🎯 PROJECT HEALTH OVERVIEW
{'─'*70}
Overall Health Score: {health.get('health_score', 0)}/100 {health.get('status_emoji', '')}
Status: {health.get('health_status', 'UNKNOWN')}

Score Breakdown:
  • Completion: {health.get('breakdown', {}).get('completion_score', 0)}/40
  • Timeline: {health.get('breakdown', {}).get('timeline_score', 0)}/30
  • Balance: {health.get('breakdown', {}).get('balance_score', 0)}/20
  • Velocity: {health.get('breakdown', {}).get('velocity_score', 0)}/10

{'─'*70}
📈 KEY METRICS
{'─'*70}
Total Tasks: {health.get('metrics', {}).get('total_tasks', 0)}
  ✅ Completed: {health.get('metrics', {}).get('completed_tasks', 0)} ({health.get('metrics', {}).get('completion_rate', 0)}%)
  🔄 In Progress: {health.get('metrics', {}).get('in_progress_tasks', 0)}
  ⚠️  Overdue: {health.get('metrics', {}).get('overdue_tasks', 0)}

Team Size: {health.get('metrics', {}).get('team_size', 0)} members

Today's Velocity: {velocity.get('tasks_completed', 0)} tasks completed
Trend: {velocity.get('trend', 'UNKNOWN')} {velocity.get('trend_emoji', '')}

{'─'*70}
👥 WORKLOAD DISTRIBUTION
{'─'*70}
Balance Status: {workload.get('balance_status', 'UNKNOWN')}
Average Tasks per Person: {workload.get('statistics', {}).get('average_tasks_per_person', 0)}

"""

        # Add overloaded members if any
        if workload.get('overloaded_members'):
            report += "⚠️  OVERLOADED TEAM MEMBERS:\n"
            for member in workload['overloaded_members'][:3]:
                report += f"  • {member['user_name']}: {member['total_tasks']} tasks ({member['overdue_tasks']} overdue)\n"
            report += "\n"
        
        # Add bottlenecks if critical
        if bottlenecks.get('severity') in ['CRITICAL', 'HIGH']:
            report += f"{'─'*70}\n"
            report += f"🚨 CRITICAL ISSUES (Severity: {bottlenecks.get('severity')})\n"
            report += f"{'─'*70}\n"
            
            if bottlenecks.get('bottlenecks', {}).get('critical_users'):
                report += "⚠️  Blocked Team Members:\n"
                for user in bottlenecks['bottlenecks']['critical_users'][:3]:
                    report += f"  • {user['user_name']}: {user['overdue_count']} overdue tasks\n"
                report += "\n"
            
            if bottlenecks.get('bottlenecks', {}).get('long_overdue_tasks'):
                report += "📅 Long Overdue Tasks:\n"
                for task in bottlenecks['bottlenecks']['long_overdue_tasks'][:3]:
                    report += f"  • {task['task_name']}: {task['days_overdue']} days overdue\n"
                report += "\n"
        
        report += f"{'='*70}\n"
        report += "End of Daily Report\n"
        report += f"{'='*70}\n"
        
        return report
        
    except Exception as e:
        return f"Error generating daily report: {str(e)}"


# ============================================================================
# WEEKLY SUMMARY
# ============================================================================

def generate_weekly_summary(project_id: str) -> str:
    """
    Generate comprehensive weekly summary.
    """
    try:
        # Gather data
        health = calculate_project_health(project_id)
        workload = analyze_team_workload_balance(project_id)
        velocity = calculate_team_velocity(project_id, days=7)
        milestones = analyze_milestone_risks(project_id)
        bottlenecks = detect_bottlenecks(project_id)
        
        report = f"""
{'='*70}
📊 WEEKLY PROJECT SUMMARY
{'='*70}
Project: {health.get('project_name', 'Unknown')}
Week Ending: {datetime.now().strftime('%B %d, %Y')}

{'─'*70}
🎯 EXECUTIVE SUMMARY
{'─'*70}
Overall Health: {health.get('health_score', 0)}/100 - {health.get('health_status', 'UNKNOWN')} {health.get('status_emoji', '')}

This Week's Progress:
  • {velocity.get('tasks_completed', 0)} tasks completed
  • Current velocity: {velocity.get('velocity_per_day', 0)} tasks/day
  • Velocity trend: {velocity.get('trend', 'UNKNOWN')} ({velocity.get('trend_percentage', 0):+.1f}%)

{'─'*70}
📈 DETAILED METRICS
{'─'*70}
Task Status:
  • Total: {health.get('metrics', {}).get('total_tasks', 0)}
  • Completed: {health.get('metrics', {}).get('completed_tasks', 0)} ({health.get('metrics', {}).get('completion_rate', 0)}%)
  • In Progress: {health.get('metrics', {}).get('in_progress_tasks', 0)}
  • Overdue: {health.get('metrics', {}).get('overdue_tasks', 0)}

Team Performance:
  • Team Size: {health.get('metrics', {}).get('team_size', 0)}
  • Avg Tasks/Person: {workload.get('statistics', {}).get('average_tasks_per_person', 0)}
  • Workload Balance: {workload.get('balance_status', 'UNKNOWN')}

{'─'*70}
🎯 MILESTONE STATUS
{'─'*70}
"""
        
        if milestones.get('milestones'):
            risk_summary = milestones.get('risk_summary', {})
            report += f"Total Active Milestones: {milestones.get('total_milestones', 0)}\n\n"
            report += "Risk Distribution:\n"
            report += f"  🔴 Critical: {risk_summary.get('CRITICAL', 0)}\n"
            report += f"  🟠 High: {risk_summary.get('HIGH', 0)}\n"
            report += f"  🟡 Medium: {risk_summary.get('MEDIUM', 0)}\n"
            report += f"  🟢 Low: {risk_summary.get('LOW', 0)}\n\n"
            
            # Show at-risk milestones
            at_risk = [m for m in milestones['milestones'] if m['risk_level'] in ['CRITICAL', 'HIGH']]
            if at_risk:
                report += "⚠️  AT-RISK MILESTONES:\n"
                for m in at_risk[:3]:
                    report += f"\n  • {m['milestone_title']}\n"
                    report += f"    Risk: {m['risk_level']}\n"
                    report += f"    Completion: {m['completion_percentage']}%\n"
                    report += f"    Days Remaining: {m.get('days_remaining', 'N/A')}\n"
                    if m.get('risk_factors'):
                        report += f"    Issues: {', '.join(m['risk_factors'][:2])}\n"
        else:
            report += "No active milestones found.\n"
        
        report += f"\n{'─'*70}\n"
        report += "👥 TEAM WORKLOAD\n"
        report += f"{'─'*70}\n"
        
        # Top 5 most loaded team members
        all_members = workload.get('all_members', [])
        if all_members:
            report += "Current Workload Distribution:\n\n"
            for member in all_members[:5]:
                report += f"  {member['user_name']}:\n"
                report += f"    • Tasks: {member['total_tasks']} ({member['overdue_tasks']} overdue)\n"
                report += f"    • Estimated Hours: {member['estimated_hours']}h\n"
        
        report += f"\n{'─'*70}\n"
        report += "🚧 BOTTLENECKS & BLOCKERS\n"
        report += f"{'─'*70}\n"
        report += f"Severity Level: {bottlenecks.get('severity', 'UNKNOWN')}\n\n"
        
        summary = bottlenecks.get('summary', {})
        report += f"  • Critical Users: {summary.get('critical_users_count', 0)}\n"
        report += f"  • Long Overdue Tasks: {summary.get('long_overdue_count', 0)}\n"
        report += f"  • Blocked High Priority: {summary.get('blocked_high_priority', 0)}\n"
        report += f"  • At-Risk Milestones: {summary.get('at_risk_milestones', 0)}\n"
        
        report += f"\n{'='*70}\n"
        report += "End of Weekly Summary\n"
        report += f"{'='*70}\n"
        
        return report
        
    except Exception as e:
        return f"Error generating weekly summary: {str(e)}"


# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================

def generate_executive_summary(project_id: str) -> str:
    """
    Brief executive summary for stakeholders.
    """
    try:
        health = calculate_project_health(project_id)
        velocity = calculate_team_velocity(project_id, days=7)
        milestones = analyze_milestone_risks(project_id)
        
        report = f"""
{'='*70}
📋 EXECUTIVE SUMMARY
{'='*70}
Project: {health.get('project_name', 'Unknown')}
Date: {datetime.now().strftime('%B %d, %Y')}

OVERALL STATUS: {health.get('health_status', 'UNKNOWN')} {health.get('status_emoji', '')}
Health Score: {health.get('health_score', 0)}/100

{'─'*70}
KEY HIGHLIGHTS
{'─'*70}

Progress:
  • {health.get('metrics', {}).get('completion_rate', 0)}% of tasks completed
  • {health.get('metrics', {}).get('completed_tasks', 0)} of {health.get('metrics', {}).get('total_tasks', 0)} tasks done
  
Current Velocity: {velocity.get('tasks_completed', 0)} tasks/week ({velocity.get('trend', 'STEADY')} {velocity.get('trend_emoji', '')})

"""
        
        # Milestone status
        risk_summary = milestones.get('risk_summary', {})
        at_risk_count = risk_summary.get('CRITICAL', 0) + risk_summary.get('HIGH', 0)
        
        if at_risk_count > 0:
            report += f"⚠️  ATTENTION REQUIRED:\n"
            report += f"  • {at_risk_count} milestone(s) at risk\n"
            report += f"  • {health.get('metrics', {}).get('overdue_tasks', 0)} task(s) overdue\n\n"
        else:
            report += "✅ All milestones on track\n\n"
        
        report += f"{'─'*70}\n"
        report += "RECOMMENDED ACTIONS:\n"
        
        # Simple recommendations
        if health.get('health_score', 0) < 60:
            report += "  1. Schedule project review meeting\n"
            report += "  2. Review and reassign overdue tasks\n"
            report += "  3. Assess team capacity and workload\n"
        elif at_risk_count > 0:
            report += "  1. Focus on at-risk milestones\n"
            report += "  2. Address bottlenecks blocking progress\n"
        else:
            report += "  • Continue current trajectory\n"
            report += "  • Monitor velocity for any changes\n"
        
        report += f"\n{'='*70}\n"
        
        return report
        
    except Exception as e:
        return f"Error generating executive summary: {str(e)}"


# ============================================================================
# TEAM PERFORMANCE REPORT
# ============================================================================

def generate_team_performance_report(project_id: str) -> str:
    """
    Detailed individual team member performance.
    """
    try:
        workload = analyze_team_workload_balance(project_id)
        velocity = calculate_team_velocity(project_id, days=7)
        
        report = f"""
{'='*70}
👥 TEAM PERFORMANCE REPORT
{'='*70}
Date: {datetime.now().strftime('%B %d, %Y')}

{'─'*70}
TEAM OVERVIEW
{'─'*70}
Team Size: {workload.get('team_size', 0)}
Workload Balance: {workload.get('balance_status', 'UNKNOWN')}
Team Velocity: {velocity.get('velocity_per_day', 0)} tasks/day

Statistics:
  • Average Tasks/Person: {workload.get('statistics', {}).get('average_tasks_per_person', 0)}
  • Total Active Tasks: {workload.get('statistics', {}).get('total_active_tasks', 0)}

{'─'*70}
INDIVIDUAL PERFORMANCE
{'─'*70}

"""
        
        all_members = workload.get('all_members', [])
        
        for i, member in enumerate(all_members, 1):
            report += f"{i}. {member['user_name']}\n"
            report += f"   Email: {member['email']}\n"
            report += f"   Current Load: {member['total_tasks']} tasks\n"
            report += f"   Overdue: {member['overdue_tasks']}\n"
            report += f"   Estimated Hours: {member['estimated_hours']}h\n"
            
            # Status indicator
            avg_tasks = workload.get('statistics', {}).get('average_tasks_per_person', 0)
            if member['total_tasks'] > avg_tasks * 1.5:
                report += f"   Status: ⚠️  OVERLOADED\n"
            elif member['total_tasks'] < avg_tasks * 0.5:
                report += f"   Status: 🟢 AVAILABLE\n"
            else:
                report += f"   Status: ✅ BALANCED\n"
            
            # Top tasks
            if member.get('task_list'):
                report += f"   Top Tasks:\n"
                for task in member['task_list'][:3]:
                    status_emoji = "⚠️" if task['is_overdue'] else "🔄"
                    report += f"     {status_emoji} {task['task_name']} ({task['status']})\n"
            
            report += "\n"
        
        report += f"{'='*70}\n"
        
        return report
        
    except Exception as e:
        return f"Error generating team report: {str(e)}"


# ============================================================================
# RISK REPORT
# ============================================================================

def generate_risk_report(project_id: str) -> str:
    """
    Comprehensive risk analysis.
    """
    try:
        health = calculate_project_health(project_id)
        bottlenecks = detect_bottlenecks(project_id)
        milestones = analyze_milestone_risks(project_id)
        
        report = f"""
{'='*70}
🚨 PROJECT RISK ANALYSIS REPORT
{'='*70}
Project: {health.get('project_name', 'Unknown')}
Date: {datetime.now().strftime('%B %d, %Y')}

{'─'*70}
OVERALL RISK ASSESSMENT
{'─'*70}
Project Health: {health.get('health_status', 'UNKNOWN')} ({health.get('health_score', 0)}/100)
Bottleneck Severity: {bottlenecks.get('severity', 'UNKNOWN')}

{'─'*70}
IDENTIFIED RISKS
{'─'*70}

1. TIMELINE RISKS
"""
        
        overdue = health.get('metrics', {}).get('overdue_tasks', 0)
        if overdue > 0:
            report += f"   🔴 HIGH: {overdue} tasks currently overdue\n"
        
        at_risk_milestones = [m for m in milestones.get('milestones', []) if m['risk_level'] in ['CRITICAL', 'HIGH']]
        if at_risk_milestones:
            report += f"   🔴 HIGH: {len(at_risk_milestones)} milestone(s) at risk of missing deadline\n"
        
        if not overdue and not at_risk_milestones:
            report += "   🟢 LOW: No significant timeline risks\n"
        
        report += "\n2. RESOURCE RISKS\n"
        
        critical_users = bottlenecks.get('bottlenecks', {}).get('critical_users', [])
        if critical_users:
            report += f"   🔴 HIGH: {len(critical_users)} team member(s) overloaded with overdue tasks\n"
            for user in critical_users[:3]:
                report += f"     • {user['user_name']}: {user['overdue_count']} overdue tasks\n"
        else:
            report += "   🟢 LOW: Team workload is manageable\n"
        
        report += "\n3. QUALITY RISKS\n"
        
        blocked_high_priority = bottlenecks.get('bottlenecks', {}).get('high_priority_blocked', [])
        if blocked_high_priority:
            report += f"   🟠 MEDIUM: {len(blocked_high_priority)} high-priority task(s) blocked\n"
        else:
            report += "   🟢 LOW: No blocked high-priority tasks\n"
        
        report += f"\n{'─'*70}\n"
        report += "RISK MITIGATION RECOMMENDATIONS\n"
        report += f"{'─'*70}\n"
        
        # Provide specific recommendations based on risks
        if critical_users:
            report += "\n1. Address Overloaded Team Members:\n"
            for user in critical_users[:2]:
                report += f"   • Reassign tasks from {user['user_name']}\n"
        
        if at_risk_milestones:
            report += "\n2. Protect At-Risk Milestones:\n"
            for m in at_risk_milestones[:2]:
                report += f"   • {m['milestone_title']}: Add resources or extend deadline\n"
        
        if overdue > 5:
            report += "\n3. Clear Overdue Backlog:\n"
            report += f"   • Prioritize and complete {overdue} overdue tasks\n"
        
        report += f"\n{'='*70}\n"
        
        return report
        
    except Exception as e:
        return f"Error generating risk report: {str(e)}"