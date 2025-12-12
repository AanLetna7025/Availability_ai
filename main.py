import os
import sys
import traceback
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
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
    generate_ai_recommendations
)
from chatbot_core.portfolio_analyzer import (
    analyze_portfolio,
    generate_portfolio_insights,
    get_all_projects
)

graph_cache = {}

# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the FastAPI application.
    """
    print("\n" + "="*60)
    print(">> FastAPI Starting Up...")
    print("="*60)
    
    startup_ok = True
    
    try:
        # Test MongoDB connection
        from chatbot_core.tools import db
        db.command('ping')
        print("[OK] MongoDB connected")
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        startup_ok = False
    
    try:
        # Test Google API Key
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            print("[OK] Google API Key found")
        else:
            print("[WARNING] Google API Key not found - AI features will be limited")
    except Exception as e:
        print(f"[WARNING] Google API check failed: {e}")
    
    if startup_ok:
        print("[OK] All startup checks passed!")
    else:
        print("[WARNING] Some startup checks failed - app may have limited functionality")
    
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n" + "="*60)
    print(">> FastAPI shutting down...")
    print("="*60)

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Project Management Intelligence API",
    description="AI-powered project management with chat, analytics, and recommendations",
    version="2.0.0",
    lifespan=lifespan
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
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def run_blocking_io(func, *args, timeout=30):
    """
    Run blocking I/O operations in thread pool with timeout.
    Prevents blocking the event loop.
    """
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, *args),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")

def validate_result(result):
    """Check if result contains error and raise HTTPException if so."""
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Simple health check for deployment platforms and monitoring.
    """
    return {"status": "ok"}


@app.get("/health/full")
async def health_check_full():
    """
    Complete health check including database connectivity.
    """
    from chatbot_core.tools import db
    
    health_data = {
        "status": "healthy",
        "service": "Project Management Intelligence API",
        "version": "2.0.0",
        "database": "unknown",
        "ai_enabled": bool(os.getenv("GOOGLE_API_KEY")),
        "timestamp": datetime.utcnow().isoformat(),
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
    
    try:
        db.command('ping')
        health_data["database"] = "connected"
    except Exception as e:
        health_data["database"] = f"error: {str(e)}"
        health_data["status"] = "degraded"
    
    return health_data

# ============================================================================
# PORTFOLIO OVERVIEW ENDPOINTS
# ============================================================================

@app.get("/api/portfolio/overview")
async def get_overview():
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
async def get_insights():
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
    """
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
                graph_cache[project_id] = await asyncio.to_thread(
                    initialize_graph_agent, 
                    project_id
                )
                print(f"✅ Graph initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize graph: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
        
        graph = graph_cache[project_id]
        thread_id = f"{request.user_id}_{project_id}"
        
        inputs = {
            "input": request.query,
            "intermediate_steps": [],
            "agent_outcome": "",
            "final_answer": ""
        }
        
        print(f"🚀 Invoking agent with thread_id: {thread_id}")
        
        response = await asyncio.wait_for(
            asyncio.to_thread(
                graph.invoke,
                inputs,
                {
                    "configurable": {"thread_id": thread_id},
                    "recursion_limit": 50
                }
            ),
            timeout=60.0
        )
        
        final_answer = response.get('final_answer', 'No answer generated')
        print(f"\n✅ Response generated: {final_answer[:100]}...\n")
        
        return {
            "response": final_answer,
            "thread_id": thread_id
        }
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Chat request timeout - please try again")
    except HTTPException:
        raise
    except Exception as e:
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
    """
    try:
        result = await run_blocking_io(calculate_project_health, project_id)
        return validate_result(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/dashboard")
async def get_project_dashboard(project_id: str):
    """
    Get all key metrics in one call for dashboard display.
    """
    try:
        health_task = run_blocking_io(calculate_project_health, project_id)
        workload_task = run_blocking_io(analyze_team_workload_balance, project_id)
        velocity_task = run_blocking_io(calculate_team_velocity, project_id, 7)
        bottlenecks_task = run_blocking_io(detect_bottlenecks, project_id)
        milestones_task = run_blocking_io(analyze_milestone_risks, project_id)
        recs_task = run_blocking_io(generate_ai_recommendations, project_id, 5)
        
        health, workload, velocity, bottlenecks, milestones, recs = await asyncio.gather(
            health_task,
            workload_task,
            velocity_task,
            bottlenecks_task,
            milestones_task,
            recs_task
        )
        
        dashboard = {
            "health": health,
            "workload": workload,
            "velocity": velocity,
            "bottlenecks": bottlenecks,
            "milestone_risks": milestones,
            }
        if recs.get("success") and "error" not in recs:
            dashboard["top_recommendations"]= recs.get("recommendations",[])
        else:
            dashboard["top_recommendations"]=[]
            if "error" in recs:
                dashboard["recommendation_error"]=recs.get("error")

        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/api/projects/{project_id}/analysis/workload")
async def analyze_workload(project_id: str):
    """Analyze team workload distribution."""
    try:
        result = await run_blocking_io(analyze_team_workload_balance, project_id)
        return validate_result(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/analysis/bottlenecks")
async def analyze_bottlenecks(project_id: str):
    """Detect project bottlenecks and blockers."""
    try:
        result = await run_blocking_io(detect_bottlenecks, project_id)
        return validate_result(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/analysis/milestones")
async def analyze_milestones(project_id: str):
    """Analyze milestone completion risks."""
    try:
        result = await run_blocking_io(analyze_milestone_risks, project_id)
        return validate_result(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/analysis/velocity")
async def get_team_velocity(
    project_id: str, 
    days: int = Query(default=7, ge=1, le=90)
):
    """Calculate team velocity and trends."""
    try:
        result = await run_blocking_io(calculate_team_velocity, project_id, days)
        return validate_result(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REPORT GENERATION ENDPOINTS
# ============================================================================

@app.get("/api/projects/{project_id}/reports/daily")
async def get_daily_report(project_id: str):
    """Generate daily project status report."""
    try:
        report = await run_blocking_io(generate_daily_report, project_id, timeout=45)
        return {
            "report": report,
            "format": "text",
            "generated_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/weekly")
async def get_weekly_report(project_id: str):
    """Generate comprehensive weekly project summary."""
    try:
        report = await run_blocking_io(generate_weekly_summary, project_id, timeout=45)
        return {
            "report": report,
            "format": "text",
            "generated_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/executive")
async def get_executive_summary(project_id: str):
    """Generate brief executive summary for stakeholders."""
    try:
        report = await run_blocking_io(generate_executive_summary, project_id, timeout=45)
        return {
            "report": report,
            "format": "text",
            "generated_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/team")
async def get_team_report(project_id: str):
    """Generate detailed team performance report."""
    try:
        report = await run_blocking_io(generate_team_performance_report, project_id, timeout=45)
        return {
            "report": report,
            "format": "text",
            "generated_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/reports/risks")
async def get_risk_report(project_id: str):
    """Generate comprehensive risk analysis report."""
    try:
        report = await run_blocking_io(generate_risk_report, project_id, timeout=45)
        return {
            "report": report,
            "format": "text",
            "generated_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@app.get("/api/projects/{project_id}/recommendations")
async def get_recommendations(
    project_id: str, 
    max_recommendations: int = Query(default=5, ge=1, le=20)
):
    """Generate AI-powered recommendations to improve project health.
       
       Query parameter:
       -Max_recommendations:maximum number to return (default:5,max:20)
       
       Reteurns:
       -List of actionable reccommendations with priority, category, action,etc.

    """
    try:    
        result = await run_blocking_io(
            generate_ai_recommendations, 
                project_id, 
                max_recommendations,
                timeout=60
            )
        
        return validate_result(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint with documentation links."""
    return {
        "message": "Project Management Intelligence API",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health"
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = "0.0.0.0"
    port = 8000
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting FastAPI on {host}:{port}")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )