# streamlit_app.py

import streamlit as st
import requests
import uuid
import os
import time

st.set_page_config(page_title="Project Chatbot", page_icon="💬", layout="wide")

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "current_project" not in st.session_state:
    st.session_state.current_project = ""
if "backend_wakeup_sent" not in st.session_state:
    st.session_state.backend_wakeup_sent = False

# API endpoint - try both localhost and 127.0.0.1
API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.title("💬 Project Management Chatbot")

# Fire wake-up request IMMEDIATELY (only once)
if not st.session_state.backend_wakeup_sent:
    try:
        # Non-blocking request to trigger backend wake-up
        requests.get(f"{API_URL}/health", timeout=0.5)
    except:
        pass  # Ignore errors, we just want to trigger the wake-up
    st.session_state.backend_wakeup_sent = True

# Now check backend with retries
def check_backend_with_retries():
    """Check backend health with multiple attempts"""
    max_attempts = 20
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                return True, attempt + 1
        except:
            pass
        
        if attempt < max_attempts - 1:
            time.sleep(3)  # Wait 3 seconds between attempts
    
    return False, max_attempts

# Check backend with progress
with st.spinner("🚀 Connecting to backend... (first load takes ~60 seconds)"):
    connected, attempts = check_backend_with_retries()

if connected:
    st.success(f"✅ Connected to API (connected after {attempts * 3} seconds)")
else:
    st.error("❌ Could not connect to backend after 60 seconds")
    st.info("Please refresh the page in a moment. The backend might still be starting.")
    st.stop()
# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    project_id = st.text_input(
        "Project ID",
        value=st.session_state.current_project,
        placeholder="Enter project ID..."
    )
    
    if project_id != st.session_state.current_project:
        st.session_state.current_project = project_id
        if project_id not in st.session_state.messages:
            st.session_state.messages[project_id] = []
    
    st.divider()
    st.caption(f"User ID: `{st.session_state.user_id[:8]}...`")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        if project_id in st.session_state.messages:
            st.session_state.messages[project_id] = []
            st.rerun()
    
    st.divider()
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    - Who are the team members?
    - What is the project status?
    - Show me overdue tasks
    - What is John's workload?
    - List all technologies used
    """)

# Main chat interface
if not project_id:
    st.info("👈 Please enter a Project ID in the sidebar to start chatting")
    st.stop()

# Display chat history
messages = st.session_state.messages.get(project_id, [])
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your project..."):
    # Add user message
    messages.append({"role": "user", "content": prompt})
    st.session_state.messages[project_id] = messages
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                st.caption(f"🔗 Connecting to: {API_URL}/chat/{project_id}")
                
                response = requests.post(
                    f"{API_URL}/chat/{project_id}",
                    json={
                        "query": prompt,
                        "user_id": st.session_state.user_id
                    },
                    timeout=60  # Increased timeout for agent processing
                )
                
                st.caption(f"📡 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    bot_response = response.json()["response"]
                    st.markdown(bot_response)
                    
                    # Add to history
                    messages.append({"role": "assistant", "content": bot_response})
                    st.session_state.messages[project_id] = messages
                else:
                    error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                    st.error(error_msg)
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to API. Make sure FastAPI is running on port 8000.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")