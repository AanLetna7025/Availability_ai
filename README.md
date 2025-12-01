# availability_ai

AI-powered project management intelligence system for **Availability**. Get instant insights across your entire project portfolio plus deep-dive analytics for individual projects using conversational AI.

## ✨ Features

### 🏠 Portfolio Overview (New!)
- **No Project ID Required** - Instant portfolio-wide insights on homepage
- **AI-Powered Analysis** - Gemini analyzes all projects simultaneously
- **Visual Dashboard** - Health scores, alerts, and trends across projects
- **Resource Intelligence** - Detect overloaded team members across projects
- **Quick Navigation** - Click any project to drill down into details

### 📊 Per-Project Features
- 💬 **AI Chatbot** - Ask questions about your project in natural language
- 📊 **Smart Dashboard** - Real-time health scores and project metrics
- 🔍 **Deep Analytics** - Workload analysis, bottleneck detection, milestone risks
- 📄 **Auto Reports** - Generate daily, weekly, executive, and risk reports
- 💡 **AI Recommendations** - Get actionable suggestions to improve project health

## Quick Start
```bash
# Clone and navigate to project
cd availability_ai

# Create and activate virtual environment
python -m venv availability
source availability/bin/activate  # Linux/Mac
availability\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Create .env with your credentials

# Run the application
python launcher.py
```

## Environment Setup

Create `.env` file:
```env
MONGO_URI=mongodb://username:password@host:port/database_name
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-2.0-flash-exp
```

## Usage

### Option 1: Launcher (Recommended)
```bash
python launcher.py
```
- Streamlit UI: `http://localhost:8501`
- API Docs: `http://localhost:8000/docs`

### Option 2: Manual
```bash
# Terminal 1
uvicorn main:app --reload --port 8000

# Terminal 2
streamlit run streamlit_app.py
```

## User Flow
```
1. Open App → Portfolio Overview (ALL projects)
   ↓
2. See health scores, alerts, AI insights
   ↓
3. Click "View Details" on any project
   ↓
4. Navigate to Dashboard/Analytics/Reports/Chatbot for deep dive
```

## Example Questions

**Portfolio-level (Homepage):**
- View all projects at once
- See which projects need attention
- Identify overloaded team members across projects
- Get AI-generated executive insights

**Project-level (Chatbot):**
- Who are the team members?
- What is the project status?
- Show me overdue tasks
- What technologies are being used?
- What is John's workload?

## Project Structure
```
availability_ai/
├── chatbot_core/
│   ├── agent.py                 # LangGraph agent
│   ├── tools.py                 # MongoDB queries
│   ├── analysis_tools.py        # Health & analytics (per-project)
│   ├── portfolio_analyzer.py    # Portfolio-wide analysis (NEW)
│   ├── report_generator.py      # Report generation
│   └── recommendation_engine.py # AI recommendations
├── main.py                      # FastAPI backend (API + Analytics)
├── streamlit_app.py             # Multi-page web interface
├── launcher.py                  # Unified startup script
├── .env                         # Environment variables
└── requirements.txt
```

## Features Overview

### 🏠 Portfolio Overview Page (New Homepage)
**No Project ID required** - Loads immediately with:
- **Portfolio Metrics**: Total projects, average health, overdue tasks, team size
- **Critical Alerts**: Projects and issues needing immediate attention
- **AI Insights**: Executive summary, key insights, recommended actions
- **Project Cards**: Visual grid showing all projects with health scores
- **Charts**: Health distribution, status breakdown, resource heatmaps
- **Resource Analysis**: Team members working across multiple projects

### 📊 Dashboard Page
- Project health score (0-100) with breakdown
- Task completion rates and velocity trends
- Team size and workload distribution
- Visual charts (pie, gauge, bar graphs)

### 💬 Chatbot Page
- Natural language queries about specific projects
- Conversation memory per user-project
- Access to 10+ project data tools

### 🔍 Analytics Page
- **Workload Analysis** - Identify overloaded/underutilized team members
- **Bottleneck Detection** - Find critical blockers and long overdue tasks
- **Milestone Risks** - Assess completion probability for each milestone
- **Velocity Tracking** - Monitor team productivity trends

### 📄 Reports Page
Generate professional reports:
- Daily status summary
- Weekly comprehensive review
- Executive brief for stakeholders
- Team performance breakdown
- Risk analysis report

### 💡 Recommendations Page
- AI-powered actionable suggestions
- Priority-based filtering (HIGH/MEDIUM/LOW)
- Expected impact and effort estimates
- Rule-based fallback for reliability

## API Endpoints

### Portfolio (New!)
- `GET /api/portfolio/overview` - All projects analysis
- `GET /api/portfolio/insights` - AI-generated portfolio insights
- `GET /api/portfolio/projects` - Simple project list

### Chatbot
**POST** `/chat/{project_id}`
```json
{
  "query": "Who are the team members?",
  "user_id": "user123"
}
```

### Analytics (Per-Project)
- `GET /api/projects/{id}/health` - Health score
- `GET /api/projects/{id}/dashboard` - Complete metrics
- `GET /api/projects/{id}/analysis/workload` - Team workload
- `GET /api/projects/{id}/analysis/bottlenecks` - Blockers
- `GET /api/projects/{id}/analysis/milestones` - Milestone risks
- `GET /api/projects/{id}/analysis/velocity` - Team velocity

### Reports
- `GET /api/projects/{id}/reports/daily` - Daily report
- `GET /api/projects/{id}/reports/weekly` - Weekly summary
- `GET /api/projects/{id}/reports/executive` - Executive brief
- `GET /api/projects/{id}/reports/team` - Team performance
- `GET /api/projects/{id}/reports/risks` - Risk analysis

### Recommendations
- `GET /api/projects/{id}/recommendations?method=ai` - AI suggestions
- `GET /api/projects/{id}/recommendations/rules` - Rule-based

### Utility
- `GET /health` - Health check
- `GET /` - API documentation

## What Makes This Different?

**Before:** 
- One project at a time
- Need Project ID to start
- No cross-project insights

**After:**
- Portfolio-wide overview on homepage
- AI analyzes ALL projects simultaneously
- Identify patterns across projects
- Resource allocation insights
- Executive-ready dashboard

## Troubleshooting

### Dependency Issues
```bash
# Update packages
pip install --upgrade langchain-core langchain-google-genai langgraph plotly pandas

# Or reinstall
pip uninstall langchain-core langchain-google-genai langgraph -y
pip install langchain-core langchain-google-genai langgraph
```

### Port Conflicts
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Test Connection
```bash
# MongoDB
python -c "from chatbot_core.tools import db; print(db.command('ping'))"

# Imports
python -c "from chatbot_core.agent import initialize_graph_agent; print('OK')"

# Portfolio Analysis
python -c "from chatbot_core.portfolio_analyzer import get_all_projects; print(f'Found {len(get_all_projects())} projects')"
```

## Tech Stack

- **FastAPI** - REST API backend
- **Streamlit** - Interactive web interface
- **LangGraph** - Agentic workflow framework
- **Google Gemini** - AI language model (Gemini 2.0 Flash)
- **MongoDB** - Database
- **Plotly** - Data visualizations
- **Python 3.11+** - Core language

## Use Cases

### For Team Leads
- Monitor all projects from one dashboard
- Identify struggling projects early
- Balance workload across teams
- Get AI-powered recommendations

### For Project Managers
- Deep-dive analytics per project
- Generate reports for stakeholders
- Track milestones and risks
- Chat with AI about project details

### For Executives
- Portfolio health at a glance
- Executive summaries
- Resource utilization insights
- Strategic recommendations

---

**Get Google API Key:** [Google AI Studio](https://makersuite.google.com/app/apikey)

**Demo:** Run `python launcher.py` and open `http://localhost:8501` to see the portfolio overview!