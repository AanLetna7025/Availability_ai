# availability_ai

AI-powered chatbot for the project management tool **Availability**. Get intelligent insights about projects, teams, tasks, and workloads using conversational AI.

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
LLM_MODEL=gemini-2.5-flash
```

## Usage

### Option 1: Launcher (Recommended)
```bash
python launcher.py
```

### Option 2: Manual
```bash
# Terminal 1
uvicorn main:app --reload --port 8000

# Terminal 2
streamlit run streamlit_app.py
```

Access at: `http://localhost:8501`

## Example Questions

- Who are the team members?
- What is the project status?
- Show me overdue tasks
- What technologies are being used?
- What is John's workload?

## Project Structure

```
availability_ai/
├── chatbot_core/
│   ├── agent.py         # LangGraph agent
│   └── tools.py         # MongoDB queries
├── main.py              # FastAPI backend
├── streamlit_app.py     # Web interface
├── launcher.py          # Startup script
├── .env                 # Environment variables
└── requirements.txt
```

## Troubleshooting

### Dependency Issues
```bash
# Update LangChain packages
pip install --upgrade langchain-core langchain-google-genai langgraph

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

## API Endpoints

**POST** `/chat/{project_id}`
```json
{
  "query": "Who are the team members?",
  "user_id": "user123"
}
```

**GET** `/health` - Health check

## Tech Stack

- FastAPI - Backend API
- Streamlit - Web interface
- LangGraph - Agent framework
- Google Gemini - AI model
- MongoDB - Database
- Python 3.11+

---

**Get Google API Key:** [Google AI Studio](https://makersuite.google.com/app/apikey)