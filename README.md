# Availability AI

> **AI-powered Project Management Intelligence System**

An intelligent project management platform that combines **real-time analytics**, **AI-driven insights**, and **conversational intelligence** to help teams optimize project health, resource allocation, and delivery timelines.

---

## 🎯 Overview

Availability AI is a comprehensive project management intelligence system that provides instant insights across your entire project portfolio and deep-dive analytics for individual projects. Built with **LangGraph agents**, **Google Gemini AI**, and **MongoDB**, it offers both portfolio-wide intelligence and granular project-level analytics through an intuitive web interface and powerful REST API.

### Key Capabilities
- **Portfolio Intelligence** - View all projects simultaneously with aggregated health metrics
- **Conversational AI** - Ask natural language questions about your projects via intelligent chatbot
- **Predictive Analytics** - Identify risks, bottlenecks, and resource constraints before they impact timelines
- **Automated Reporting** - Generate daily, weekly, executive, team, and risk reports
- **Real-time Monitoring** - Track project health, team velocity, and milestone progress
- **AI Recommendations** - Receive actionable suggestions to improve project outcomes

---

## ✨ Features

### 🏠 Portfolio Overview Dashboard
- **No Project ID Required** - View all active projects on the homepage instantly
- **Aggregated Health Metrics** - Portfolio-wide health score, status alerts, and critical issues
- **Executive Insights** - AI-generated portfolio summary with key findings and trends
- **Resource Intelligence** - Identify overloaded team members across all projects
- **Project Quick View** - See status, client, and key metrics for each project at a glance
- **Drill-Down Navigation** - Click any project to access detailed analytics

### 🤖 AI-Powered Chatbot (Per-Project)
- **Natural Language Queries** - Ask questions about your project in plain English
- **Contextual Understanding** - Agent understands project context and provides relevant answers
- **LangGraph State Management** - Maintains conversation history per user-project combination
- **Real-time Data Access** - Pulls live data from MongoDB for current project information
- **Example Questions:**
  - "Who are the team members?"
  - "What is the project status?"
  - "Show me overdue tasks"
  - "What technologies are being used?"
  - "What is [person's name]'s workload?"
  - "Which milestones are at risk?"

### 📊 Project Health Analysis
- **Health Score (0-100)** - Multi-factor health calculation based on:
  - Task completion rate (40%)
  - Timeline adherence (30%)
  - Workload balance (20%)
  - Team velocity (10%)
- **Health Status Categories** - EXCELLENT, GOOD, AT_RISK, CRITICAL
- **Detailed Metrics Breakdown** - Key performance indicators with historical trends

### 📈 Advanced Analytics Suite
- **Workload Balance Analysis** - Identify underutilized and overloaded team members
- **Bottleneck Detection** - Find critical blockers and dependencies slowing projects
- **Milestone Risk Analysis** - Assess completion risk for upcoming milestones
- **Team Velocity Tracking** - Calculate task completion trends (7, 14, 30-day periods)
- **Trend Analysis** - Identify ACCELERATING, STEADY, or SLOWING velocity patterns

### 📄 Automated Report Generation
- **Daily Reports** - Quick status updates with health metrics and critical issues
- **Weekly Summaries** - Comprehensive progress overview with team performance
- **Executive Summaries** - Concise stakeholder-ready status and recommendations
- **Team Performance Reports** - Individual metrics for all team members
- **Risk Reports** - Detailed analysis of critical issues and risks
- **Perfect for:**
  - Daily standup meetings
  - Email digests and Slack notifications
  - Stakeholder updates
  - Board meetings
  - Project retrospectives

### 💡 Intelligent Recommendations
- **AI-Generated Suggestions** - Gemini provides personalized improvement recommendations
- **Rule-Based Recommendations** - Predefined logic-based suggestions
- **Priority Levels** - HIGH, MEDIUM, LOW severity recommendations
- **Actionable Insights** - Specific, implementable recommendations to improve project health

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB instance with project data
- Google API Key (for Gemini AI)
- Git (optional)

### Installation

```bash
# 1. Navigate to project directory
cd availability_ai

# 2. Create virtual environment
python -m venv availability

# 3. Activate virtual environment
# On Windows:
availability\Scripts\activate
# On macOS/Linux:
source availability/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
# Create .env file in the project root with:
MONGO_URI=mongodb://username:password@host:port/database_name
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-2.5-flash  # or latest Gemini model
```

### Running the Application

#### Option 1: Using Launcher (Recommended)
```bash
python launcher.py
```
This starts both services automatically:
- **Streamlit UI**: http://localhost:8501
- **FastAPI Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

#### Option 2: Manual Startup (Two Terminals)
```bash
# Terminal 1 - Start FastAPI backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Start Streamlit frontend
streamlit run streamlit_app.py
```

---

## 📋 Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB Connection
MONGO_URI=mongodb://username:password@localhost:27017/project_management

# Google Generative AI
GOOGLE_API_KEY=your_google_api_key_here

# LLM Model (Optional - defaults to gemini-2.5-flash)
LLM_MODEL=gemini-2.0-flash-exp

# FastAPI URL (Optional - used by Streamlit)
FASTAPI_URL=http://127.0.0.1:8000

# Deployment (Optional)
PORT=8501  # Set for production deployment (e.g., Render, Railway)
```

### Environment Setup Guide

**For Local Development:**
```env
MONGO_URI=mongodb://127.0.0.1:27017/availability
GOOGLE_API_KEY=your_api_key
```

**For Production Deployment:**
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database
GOOGLE_API_KEY=your_api_key
PORT=8501  # Platform will set this automatically
```

---

## 💻 Architecture

### Technology Stack
- **Backend**: FastAPI (async Python framework)
- **Frontend**: Streamlit (rapid web UI development)
- **AI/LLM**: Google Generative AI (Gemini)
- **Agent Framework**: LangGraph (multi-step reasoning)
- **Database**: MongoDB (document-oriented)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Altair

### System Architecture

```
┌─────────────────────┐
│   Streamlit UI      │ (Port 8501)
│  - Portfolio View   │
│  - Project Details  │
│  - Dashboards       │
└──────────┬──────────┘
           │ HTTP Requests
           ▼
┌─────────────────────────────────────┐
│       FastAPI Backend (Port 8000)   │
├─────────────────────────────────────┤
│  Portfolio Endpoints                │
│  ├─ /api/portfolio/overview         │
│  ├─ /api/portfolio/insights         │
│  └─ /api/portfolio/projects         │
│                                     │
│  Project Endpoints                  │
│  ├─ /api/projects/{id}/health      │
│  ├─ /api/projects/{id}/dashboard   │
│  └─ /api/projects/{id}/analysis/*  │
│                                     │
│  Report Endpoints                   │
│  ├─ /reports/daily                  │
│  ├─ /reports/weekly                 │
│  ├─ /reports/executive              │
│  ├─ /reports/team                   │
│  └─ /reports/risks                  │
│                                     │
│  Chat Endpoint                      │
│  └─ POST /chat/{project_id}         │
└──────────┬──────────────────────────┘
           │
      ┌────┴─────┬──────────────────┐
      ▼          ▼                  ▼
   ┌──────┐  ┌──────────┐  ┌──────────────┐
   │ Mono │  │ LangGraph│  │Google Gemini │
   │ DB   │  │ Agents   │  │     AI       │
   └──────┘  └──────────┘  └──────────────┘
```

### Core Modules

```
availability_ai/
├── main.py                          # FastAPI app with all endpoints
├── launcher.py                      # Application launcher script
├── streamlit_app.py                 # Streamlit UI
├── requirements.txt                 # Python dependencies
│
└── chatbot_core/                    # Core intelligence modules
    ├── agent.py                     # LangGraph-based conversational agent
    ├── tools.py                     # MongoDB data fetching tools (10+ query functions)
    ├── analysis_tool.py             # Analytics engine (6+ analysis functions)
    ├── portfolio_analyzer.py         # Portfolio-wide analysis
    ├── report_generator.py           # Report generation (5 report types)
    ├── recommendation_engine.py      # AI recommendations
    └── __pycache__/                 # Python cache
```

---

## 📡 API Endpoints

### Health Check
```
GET /health                         # Simple health check
GET /health/full                    # Complete health check with DB status
```

### Portfolio Endpoints
```
GET /api/portfolio/overview         # Portfolio-wide analysis
GET /api/portfolio/insights         # AI-generated portfolio insights
GET /api/portfolio/projects         # List all active projects
```

### Chat Endpoint
```
POST /chat/{project_id}             # AI chatbot conversation
Request: { "query": "string", "user_id": "string" }
Response: { "response": "string", "thread_id": "string" }
```

### Project Health & Status
```
GET /api/projects/{project_id}/health       # Project health score (0-100)
GET /api/projects/{project_id}/dashboard    # Comprehensive dashboard metrics
```

### Analysis Endpoints
```
GET /api/projects/{project_id}/analysis/workload      # Team workload analysis
GET /api/projects/{project_id}/analysis/bottlenecks   # Bottleneck detection
GET /api/projects/{project_id}/analysis/milestones    # Milestone risk analysis
GET /api/projects/{project_id}/analysis/velocity      # Team velocity trends
```

### Report Generation
```
GET /api/projects/{project_id}/reports/daily          # Daily status report
GET /api/projects/{project_id}/reports/weekly         # Weekly summary
GET /api/projects/{project_id}/reports/executive      # Executive summary
GET /api/projects/{project_id}/reports/team           # Team performance report
GET /api/projects/{project_id}/reports/risks          # Risk analysis report
```

**Full API documentation available at**: `http://localhost:8000/docs` (Swagger UI)

---

## 🎯 User Workflows

### Portfolio Overview Workflow
```
1. Open application → Homepage
   ↓
2. View portfolio overview (all projects)
   ├─ Health scores, alerts, and trends
   ├─ Team resource utilization
   └─ AI-generated insights
   ↓
3. Click "View Details" on any project
   ↓
4. Access project-level features (Dashboard, Analytics, Reports, Chatbot)
```

### Project Deep-Dive Workflow
```
1. Select a specific project
   ↓
2. View Project Dashboard
   ├─ Health score and status
   ├─ Team workload distribution
   ├─ Velocity trends
   └─ Top recommendations
   ↓
3. Access Detailed Analytics
   ├─ Workload balance analysis
   ├─ Bottleneck detection
   ├─ Milestone risk assessment
   └─ Team velocity trends
   ↓
4. Generate Reports
   ├─ Daily status updates
   ├─ Weekly summaries
   ├─ Executive reports
   ├─ Team performance
   └─ Risk assessments
   ↓
5. Ask Chatbot Questions
   └─ Natural language queries about project details
```

---

## 🗂️ Project Structure
```
availability_ai/
├── chatbot_core/
│   ├── agent.py                 # LangGraph agent for conversational AI
│   ├── tools.py                 # MongoDB data fetching tools (10+ functions)
│   ├── analysis_tool.py         # Health & analytics calculations
│   ├── portfolio_analyzer.py     # Portfolio-wide analysis
│   ├── recommendation_engine.py  # AI and rule-based recommendations
│   ├── report_generator.py       # Report generation (5 report types)
│   └── __pycache__/             # Python bytecode cache
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

## API Endpoints

### Portfolio
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