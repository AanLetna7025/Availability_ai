# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from chatbot_core.agent import initialize_graph_agent

from chatbot_core.report_generator import (
    generate_daily_report,
    generate_weekly_summary,
    generate_executive_summary,
    generate_team_performance_report,
    generate_risk_report
)

from chatbot_core.analysis_tool import (
    analyze_team_workload_balance,
    detect_bottlenecks,
    analyze_milestone_risks,
    calculate_team_velocity,
    calculate_project_health
)

from chatbot_core.recommendation_engine import (
    generate_ai_recommendations,
    generate_rule_based_recommendations
)

from chatbot_core.portfolio_analyzer import (
    analyze_portfolio,
    generate_portfolio_insights,
    get_all_projects
)

load_dotenv()

# Cache for graph instances (one per project)
graph_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*60)
    print("🚀 FastAPI Starting Up...")
    print("="*60)
    try:
        # Test MongoDB connection
        from chatbot_core.tools import db
        db.command('ping')
        print("✅ MongoDB connected")
        
        # Test Google API Key
        import os
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            print("✅ Google API Key found")
        else:
            print("⚠️  Google API Key not found!")
            
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n🛑 FastAPI shutting down...")

app = FastAPI(
    title="Project Management Intelligence API",
    description="AI-powered project management with chat, analytics, and recommendations",
    version="2.0.0"
)

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST MODELS
# ============================================================================

class ChatRequest(BaseModel):
    query: str
    user_id: str

# ============================================================================
# PORTFOLIO OVERVIEW ENDPOINTS
# ============================================================================

@app.get("/api/portfolio/overview")
async def get_portfolio_overview():
    """
    Get portfolio-wide analysis of all projects.
    Perfect for the homepage dashboard - no project ID needed!
    
    Returns:
    - Total projects count
    - Portfolio health score
    - Aggregated metrics
    - Project summaries
    - Critical alerts
    - Resource insights
    
    Example:
    GET /api/portfolio/overview
    """
    try:
        portfolio_data = analyze_portfolio()
        if "error" in portfolio_data:
            return portfolio_data
        return portfolio_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/insights")
async def get_portfolio_insights():
    """
    Get AI-generated insights about the entire portfolio.
    
    Returns:
    - Executive summary
    - Key insights
    - Immediate actions needed
    - Positive trends
    
    Example:
    GET /api/portfolio/insights
    """
    try:
        portfolio_data = analyze_portfolio()
        if "error" in portfolio_data:
            raise HTTPException(status_code=404, detail=portfolio_data["error"])
        
        insights = generate_portfolio_insights(portfolio_data)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/projects")
async def list_all_projects():
    """
    Get a simple list of all active projects.
    
    Returns:
    - Project IDs
    - Project names
    - Client names
    - Basic info
    
    Example:
    GET /api/portfolio/projects
    """
    try:
        projects = get_all_projects()
        return {
            "total": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CHATBOT ENDPOINTS
# ============================================================================

@app.post("/chat/{project_id}")
async def chat_with_project(project_id: str, request: ChatRequest):
    """
    Chat endpoint with conversation memory per user-project combination.
    
    Use this to ask questions about your project like:
    - "What tasks are overdue?"
    - "Show me team workload"
    - "What's the project status?"
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        print(f"\n{'='*60}")
        print(f"📨 QUERY: {request.query}")
        print(f"👤 USER: {request.user_id}")
        print(f"📁 PROJECT: {project_id}")
        print(f"{'='*60}\n")
        
        # Get or create graph for this project
        if project_id not in graph_cache:
            print(f"🔧 Initializing new graph for project: {project_id}")
            try:
                graph_cache[project_id] = initialize_graph_agent(project_id)
                print(f"✅ Graph initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize graph: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
        
        graph = graph_cache[project_id]
        
        # Unique thread per user-project
        thread_id = f"{request.user_id}_{project_id}"
        
        # Run the agent
        inputs = {
            "input": request.query,
            "intermediate_steps": [],
            "agent_outcome": "",
            "final_answer": ""
        }
        
        print(f"🚀 Invoking agent with thread_id: {thread_id}")
        response = graph.invoke(
            inputs,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 50
            }
        )
        
        final_answer = response.get('final_answer', 'No answer generated')
        
        print(f"\n✅ Response generated: {final_answer[:100]}...\n")
        
        return {
            "response": final_answer,
            "thread_id": thread_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error: {str(e)}")
        print(f"📋 Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


# ============================================================================
# PROJECT HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/api/projects/{project_id}/health")
async def get_project_health(project_id: str):
    """
    Get overall project health score and status.
    
    Returns:
    - health_score (0-100)
    - health_status (EXCELLENT/GOOD/AT_RISK/CRITICAL)
    - Detailed breakdown by category
    - Key metrics (tasks, completion rate, team size)
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/health
    """
    try:
        result = calculate_project_health(project_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/dashboard")
async def get_project_dashboard(project_id: str):
    """
    Get all key metrics in one call for dashboard display.
    Perfect for building admin dashboards.
    
    Returns:
    - Project health
    - Task status
    - Team workload
    - Recent velocity
    - Top 3 recommendations
    - Critical issues
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/dashboard
    """
    try:
        dashboard = {
            "health": calculate_project_health(project_id),
            "workload": analyze_team_workload_balance(project_id),
            "velocity": calculate_team_velocity(project_id, days=7),
            "bottlenecks": detect_bottlenecks(project_id),
            "milestone_risks": analyze_milestone_risks(project_id),
        }
        
        # Get top 3 quick recommendations
        recs = generate_rule_based_recommendations(project_id)
        dashboard["top_recommendations"] = recs.get("recommendations", [])[:3]
        
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/api/projects/{project_id}/analysis/workload")
async def analyze_workload(project_id: str):
    """
    Analyze team workload distribution.
    
    Returns:
    - Workload per team member
    - Overloaded/underutilized members
    - Balance status
    - Task distribution statistics
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/analysis/workload
    """
    try:
        result = analyze_team_workload_balance(project_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/analysis/bottlenecks")
async def analyze_bottlenecks(project_id: str):
    """
    Detect project bottlenecks and blockers.
    
    Returns:
    - Critical users causing delays
    - Long overdue tasks (>14 days)
    - High priority blocked tasks
    - Milestone risks
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/analysis/bottlenecks
    """
    try:
        result = detect_bottlenecks(project_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/analysis/milestones")
async def analyze_milestones(project_id: str):
    """
    Analyze milestone completion risks.
    
    Returns:
    - Risk level per milestone (CRITICAL/HIGH/MEDIUM/LOW)
    - Completion percentages
    - Days remaining
    - Overdue task counts
    - Risk factors
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/analysis/milestones
    """
    try:
        result = analyze_milestone_risks(project_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/analysis/velocity")
async def get_team_velocity(project_id: str, days: Optional[int] = 7):
    """
    Calculate team velocity and trends.
    
    Query Parameters:
    - days: Number of days to analyze (default: 7)
    
    Returns:
    - Tasks completed in period
    - Velocity per day
    - Velocity per person per day
    - Trend (ACCELERATING/STEADY/SLOWING)
    - Trend percentage
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/analysis/velocity?days=14
    """
    try:
        result = calculate_team_velocity(project_id, days)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# REPORT GENERATION ENDPOINTS
# ============================================================================

@app.get("/api/projects/{project_id}/reports/daily")
async def get_daily_report(project_id: str):
    """
    Generate daily project status report.
    
    Returns formatted text report including:
    - Project health overview
    - Key metrics
    - Team velocity
    - Critical issues
    - Workload balance
    
    Perfect for:
    - Daily standup meetings
    - Email digests
    - Slack notifications
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/reports/daily
    """
    try:
        report = generate_daily_report(project_id)
        return {
            "report": report,
            "format": "text",
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/weekly")
async def get_weekly_report(project_id: str):
    """
    Generate comprehensive weekly project summary.
    
    Returns detailed weekly report with:
    - Executive summary
    - Progress overview
    - Team performance
    - Milestone status
    - Bottlenecks & blockers
    
    Perfect for:
    - Weekly team reviews
    - Stakeholder updates
    - Project retrospectives
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/reports/weekly
    """
    try:
        report = generate_weekly_summary(project_id)
        return {
            "report": report,
            "format": "text",
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/executive")
async def get_executive_summary(project_id: str):
    """
    Generate brief executive summary for stakeholders.
    
    Returns concise summary with:
    - Overall status
    - Key highlights
    - Critical issues
    - Recommended actions
    
    Perfect for:
    - C-level updates
    - Board meetings
    - Quick status checks
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/reports/executive
    """
    try:
        report = generate_executive_summary(project_id)
        return {
            "report": report,
            "format": "text",
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/team")
async def get_team_report(project_id: str):
    """
    Generate detailed team performance report.
    
    Returns individual performance metrics for all team members:
    - Current workload
    - Task counts
    - Overdue tasks
    - Top active tasks
    - Availability status
    
    Perfect for:
    - Team reviews
    - Resource planning
    - Performance discussions
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/reports/team
    """
    try:
        report = generate_team_performance_report(project_id)
        return {
            "report": report,
            "format": "text",
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/risks")
async def get_risk_report(project_id: str):
    """
    Generate comprehensive risk analysis report.
    
    Returns detailed analysis of:
    - Timeline risks
    - Resource risks
    - Quality risks
    - Risk mitigation recommendations
    
    Perfect for:
    - Risk management meetings
    - Project audits
    - Escalation documentation
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/reports/risks
    """
    try:
        report = generate_risk_report(project_id)
        return {
            "report": report,
            "format": "text",
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@app.get("/api/projects/{project_id}/recommendations")
async def get_recommendations(
    project_id: str, 
    method: Optional[str] = "ai",
    max_recommendations: Optional[int] = 5
):
    """
    Generate AI-powered recommendations to improve project health.
    
    Query Parameters:
    - method: "ai" (uses Gemini LLM) or "rules" (rule-based, faster)
    - max_recommendations: Maximum number to return (default: 5)
    
    Returns:
    - List of actionable recommendations
    - Priority levels (HIGH/MEDIUM/LOW)
    - Expected impact
    - Required effort
    - Category (WORKLOAD/TIMELINE/QUALITY/TEAM/PROCESS)
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/recommendations?method=ai&max_recommendations=3
    """
    try:
        if method.lower() == "ai":
            result = generate_ai_recommendations(project_id, max_recommendations)
        else:
            result = generate_rule_based_recommendations(project_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/recommendations/rules")
async def get_rule_based_recommendations(project_id: str):
    """
    Generate rule-based recommendations (no AI).
    
    Faster and more deterministic than AI recommendations.
    Good for:
    - Quick insights
    - Automated monitoring
    - When AI quota is limited
    
    Returns same structure as /recommendations but uses
    deterministic rules instead of LLM.
    
    Example:
    GET /api/projects/507f1f77bcf86cd799439011/recommendations/rules
    """
    try:
        result = generate_rule_based_recommendations(project_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """
    API health check endpoint.
    
    Returns service status and available features.
    """
    return {
        "status": "healthy",
        "service": "Project Management Intelligence API",
        "version": "2.0.0",
        "features": [
            "ai_chatbot",
            "project_health_analysis",
            "workload_analysis",
            "bottleneck_detection",
            "milestone_risk_analysis",
            "velocity_tracking",
            "report_generation",
            "ai_recommendations"
        ]
    }


@app.get("/")
async def root():
    """
    API root endpoint with documentation links.
    """
    return {
        "message": "Project Management Intelligence API",
        "version": "2.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "chat": {
                "path": "/chat/{project_id}",
                "method": "POST",
                "description": "Chat with AI assistant about project"
            },
            "health": {
                "path": "/api/projects/{project_id}/health",
                "method": "GET",
                "description": "Get project health score"
            },
            "dashboard": {
                "path": "/api/projects/{project_id}/dashboard",
                "method": "GET",
                "description": "Get complete dashboard data"
            },
            "analysis": {
                "workload": "/api/projects/{project_id}/analysis/workload",
                "bottlenecks": "/api/projects/{project_id}/analysis/bottlenecks",
                "milestones": "/api/projects/{project_id}/analysis/milestones",
                "velocity": "/api/projects/{project_id}/analysis/velocity"
            },
            "reports": {
                "daily": "/api/projects/{project_id}/reports/daily",
                "weekly": "/api/projects/{project_id}/reports/weekly",
                "executive": "/api/projects/{project_id}/reports/executive",
                "team": "/api/projects/{project_id}/reports/team",
                "risks": "/api/projects/{project_id}/reports/risks"
            },
            "recommendations": {
                "ai": "/api/projects/{project_id}/recommendations?method=ai",
                "rules": "/api/projects/{project_id}/recommendations/rules"
            }
        }
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)