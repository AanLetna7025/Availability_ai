# availability_ai

AI-powered chatbot for the project management tool **Availability**. Get intelligent insights about projects, teams, tasks, and workloads using conversational AI.

## ✨ Features (all works only within particular project_id)

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

## Example Questions

**Chatbot queries:**
- Who are the team members?
- What is the project status?
- Show me overdue tasks
- What technologies are being used?
- What is John's workload?

**API endpoints:**
- `GET /api/projects/{id}/health` - Get health score (0-100)
- `GET /api/projects/{id}/dashboard` - Complete metrics
- `GET /api/projects/{id}/recommendations` - AI suggestions
- `GET /api/projects/{id}/reports/daily` - Generate reports

## Project Structure
```
availability_ai/
├── chatbot_core/
│   ├── agent.py                 # LangGraph agent
│   ├── tools.py                 # MongoDB queries
│   ├── analysis_tools.py        # Health & analytics
│   ├── report_generator.py      # Report generation
│   └── recommendation_engine.py # AI recommendations
├── main.py                      # FastAPI backend (API + Analytics)
├── streamlit_app.py             # Multi-page web interface
├── launcher.py                  # Unified startup script
├── .env                         # Environment variables
└── requirements.txt
```

## Features Overview

### 📊 Dashboard Page
- Project health score (0-100) with breakdown
- Task completion rates and velocity trends
- Team size and workload distribution
- Visual charts (pie, gauge, bar graphs)

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

### Chatbot
**POST** `/chat/{project_id}`
```json
{
  "query": "Who are the team members?",
  "user_id": "user123"
}
```

### Analytics
- `GET /api/projects/{id}/health` - Health score
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
```

## Tech Stack

- **FastAPI** - REST API backend
- **Streamlit** - Interactive web interface
- **LangGraph** - Agentic workflow framework
- **Google Gemini** - AI language model
- **MongoDB** - Database
- **Plotly** - Data visualizations
- **Python 3.11+** - Core language

---

**Get Google API Key:** [Google AI Studio](https://makersuite.google.com/app/apikey)