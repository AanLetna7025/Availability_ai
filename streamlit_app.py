# streamlit_app.py

import streamlit as st
import requests
import uuid
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time




# Page config
st.set_page_config(
    page_title="Project Management AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "current_project" not in st.session_state:
    st.session_state.current_project = ""

# API endpoint
API_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    /* Fix metric box text visibility */
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
    }
    
    /* Make metric labels dark and visible */
    .stMetric label {
        color: #1f2937 !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    /* Make metric values dark and bold */
    .stMetric [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-size: 1.875rem !important;
        font-weight: 700 !important;
    }
    
    /* Make delta text visible */
    .stMetric [data-testid="stMetricDelta"] {
        color: #374151 !important;
        font-weight: 500 !important;
    }
    
    /* Recommendation boxes with proper text colors */
    .recommendation-high {
        border-left: 4px solid #ef4444;
        padding: 10px;
        margin: 10px 0;
        background-color: #fee;
        color: #991b1b !important;
    }
    
    .recommendation-medium {
        border-left: 4px solid #f59e0b;
        padding: 10px;
        margin: 10px 0;
        background-color: #fffbeb;
        color: #92400e !important;
    }
    
    .recommendation-low {
        border-left: 4px solid #22c55e;
        padding: 10px;
        margin: 10px 0;
        background-color: #f0fdf4;
        color: #14532d !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def check_api_health():
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/health", timeout=10)
            if response.status_code == 200:
                return True
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"[RETRY] API health check attempt {attempt + 1}/{max_retries}")
                time.sleep(retry_delay)
                continue
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
    
    return False

if not check_api_health():
    st.error("❌ Cannot connect to backend API. Waiting for FastAPI to start...")
    st.info("If this persists, check that FastAPI is running on port 8000.")
    st.stop()

# ============================================================================
# SIDEBAR - PROJECT SELECTION & NAVIGATION
# ============================================================================
with st.sidebar:
    st.image("https://cdn3d.iconscout.com/3d/premium/thumb/ai-robot-character-standing-at-attention-with-smiling-face-3d-icon-png-download-11431326.png", width=80)
    st.title("Navigation")
    
    # Project ID input
    project_id = st.text_input(
        "Project ID",
        value=st.session_state.current_project,
        placeholder="Enter project ID here...",
        help="Enter your project Id"
    )
    
    if project_id != st.session_state.current_project:
        st.session_state.current_project = project_id
        if project_id not in st.session_state.messages:
            st.session_state.messages[project_id] = []
        st.rerun()
    st.divider()

    # Page navigation
    if project_id:
        st.markdown("### 📂 Project Menu")
        page = st.radio(
            "Select View",
            [
                "💬 AI Chatbot",
                "📊 Dashboard",
                "🔍 Analytics",
                "📄 Reports",
                "💡 Recommendations"
            ],
            label_visibility="collapsed"
        )
        
        # Clear project button
        if st.button("← Back to Portfolio", width="stretch"):
            st.session_state.current_project = ""
            st.rerun()
        
        # Clear chat button (only on chatbot page)
        if page == "💬 AI Chatbot":
            if st.button("🗑️ Clear Chat", width="stretch"):
                if project_id in st.session_state.messages:
                    st.session_state.messages[project_id] = []
                    st.rerun()
    else:
        # No project ID - show portfolio overview info
        st.info(" **Portfolio Overview Mode**\n\nEnter a Project ID above to view project details.")
        page = " Portfolio Overview"  # Default to homepage
    
    st.divider()
    
    # User info
    st.caption(f"👤 User: `{st.session_state.user_id[:8]}...`")
    st.caption(f"🔗 API: `{API_URL}`")


    
# ============================================================================
# HELPER FUNCTION FOR ALL PROJECTS
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_overview():
    try:
        response = requests.get(f"{API_URL}/api/portfolio/overview", timeout=60)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=300)
def get_insights():
    try:
        response = requests.get(f"{API_URL}/api/portfolio/insights", timeout=120)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=300)
def list_all_projects():
    try:
        response = requests.get(f"{API_URL}/api/portfolio/projects", timeout=20)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}
    
# ============================================================================
# HELPER FUNCTIONS FOR API CALLS
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_project_health(proj_id):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/health", timeout=20)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=300)
def get_workload_analysis(proj_id):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/analysis/workload", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=300)
def get_bottlenecks(proj_id):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/analysis/bottlenecks", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=300)
def get_milestone_risks(proj_id):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/analysis/milestones", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=300)
def get_velocity(proj_id, days=7):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/analysis/velocity?days={days}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=300)
def get_recommendations(proj_id, method="ai"):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/recommendations?method={method}", timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

def get_report(proj_id, report_type):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/reports/{report_type}", timeout=20)
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# PAGE 0 : ALL PROJECTS HOMEPAGE
# ============================================================================

if not project_id or page == " Portfolio Overview":
    st.title("ALL PROJECTS OVERVIEW")
    st.markdown("**Welcome!** Get instant insights across all your projects.")
    
    # Refresh button
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🔄 Refresh", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    # Load portfolio data
    with st.spinner("🔍 Analyzing ..."):
        portfolio_data = get_overview()
        insights_data = get_insights()
    
    if "error" in portfolio_data:
        st.error(f"❌ Error loading portfolio: {portfolio_data['error']}")
        st.info("Make sure you have active projects in your database.")
        st.stop()
    
    # =========================
    # SECTION 1: Key Metrics
    # =========================
    st.subheader("📊 Portfolio at a Glance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            "Total Projects",
            portfolio_data.get('total_projects', 0),
            help="Active projects in portfolio"
        )
    
    with col2:
        portfolio_health = portfolio_data.get('portfolio_health', 0)
        if portfolio_health >= 70:
            emoji = "🟢"
        elif portfolio_health >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        st.metric(
            "Portfolio Health",
            f"{portfolio_health}/100 {emoji}",
            help="Average health across all projects"
        )
    
    with col3:
        agg = portfolio_data.get('aggregated_metrics', {})
        completion = agg.get('avg_completion_rate', 0)
        st.metric(
            "Avg Completion",
            f"{completion}%",
            help="Average task completion rate"
        )
    
    with col4:
        overdue = agg.get('total_overdue', 0)
        st.metric(
            "Overdue Tasks",
            overdue,
            delta=f"-{overdue}" if overdue > 0 else "0",
            delta_color="inverse",
            help="Total overdue tasks across portfolio"
        )
    
    with col5:
        st.metric(
            "Team Members",
            agg.get('total_team_members', 0),
            help="Total team members across all projects"
        )
    
    st.divider()
    
    # =========================
    # SECTION 2: Critical Alerts
    # =========================
    critical_alerts = portfolio_data.get('critical_alerts', [])
    
    if critical_alerts:
        st.subheader("🚨 Needs Immediate Attention")
        
        for alert in critical_alerts:
            severity = alert.get('severity', 'INFO')
            message = alert.get('message', '')
            category = alert.get('category', 'GENERAL')
            
            if severity == 'HIGH':
                st.error(f"**{category}**: {message}")
            elif severity == 'MEDIUM':
                st.warning(f"**{category}**: {message}")
            else:
                st.info(f"**{category}**: {message}")
        
        st.divider()
    
    # =========================
    # SECTION 3: AI Insights
    # =========================

    st.subheader("💡 AI-Generated Insights")

    print(f"[DEBUG] Insights response: {insights_data}")  # ← ADD DEBUG LOG

    if "error" in insights_data:
        # API returned an error
        error_msg = insights_data['error']
        st.error(f"❌ AI insights failed: {error_msg}")
        st.info("Showing rule-based analysis instead...")
        
    elif not insights_data.get('success', False):
        # API didn't return success flag
        st.warning("⚠️ AI insights unavailable (empty response)")
        st.info("Showing rule-based analysis instead...")

    else:
        # Success! Display insights
        try:
            insights = insights_data.get('insights', {})
            
            if not insights:
                st.warning("AI returned empty insights")
            else:
                # Executive Summary
                exec_summary = insights.get('executive_summary', '')
                if exec_summary:
                    st.markdown("**📋 Executive Summary:**")
                    st.info(exec_summary)
                
                # Key Insights & Actions
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🔍 Key Insights:**")
                    key_insights = insights.get('key_insights', [])
                    if key_insights:
                        for insight in key_insights:
                            st.markdown(f"✓ {insight}")
                    else:
                        st.markdown("_No specific insights_")
                
                with col2:
                    st.markdown("**✅ Immediate Actions:**")
                    actions = insights.get('immediate_actions', [])
                    if actions:
                        for action in actions:
                            st.markdown(f"→ {action}")
                    else:
                        st.markdown("_No immediate actions needed_")
                
                # Positive Trends
                trends = insights.get('positive_trends', [])
                if trends:
                    st.success("**🎉 Positive Trends:**")
                    for trend in trends:
                        st.markdown(f"📈 {trend}")
        
        except Exception as e:
            st.error(f"Error displaying insights: {str(e)}")
    st.divider()
    
    # =========================
    # SECTION 4: Project Grid
    # =========================
    st.subheader("📂 Projects")
    
    # Status filter
    status_filter = st.multiselect(
        "Filter by Status",
        ["CRITICAL", "AT_RISK", "GOOD", "EXCELLENT"],
        default=["CRITICAL", "AT_RISK", "GOOD", "EXCELLENT"]
    )
    
    projects = portfolio_data.get('projects', [])
    filtered_projects = [p for p in projects if p.get('health_status') in status_filter]
    
    if not filtered_projects:
        st.info("No projects match the selected filters")
    else:
        # Create project cards in grid
        cols_per_row = 3
        rows = [filtered_projects[i:i + cols_per_row] for i in range(0, len(filtered_projects), cols_per_row)]
        
        for row in rows:
            cols = st.columns(cols_per_row)
            
            for col, project in zip(cols, row):
                with col:
                    # Project card
                    status_emoji = project.get('status_emoji', '⚪')
                    health_score = project.get('health_score', 0)
                    
                    # Card styling
                    if health_score >= 70:
                        border_color = "#22c55e"
                    elif health_score >= 50:
                        border_color = "#f59e0b"
                    else:
                        border_color = "#ef4444"
                    
                    st.markdown(f"""
                    <div style="
                        border-left: 4px solid {border_color};
                        padding: 15px;
                        background-color: #f9fafb;
                        border-radius: 8px;
                        margin-bottom: 10px;
                    ">
                        <h4 style="color:black">{status_emoji} {project.get('project_name', 'Unnamed')}</h4>
                        <p style="color: #666; font-size: 0.9em;">Client: {project.get('client', 'N/A')}</p>
                        <p style="color: #999; font-size: 0.75em; margin-top: 8px; word-break: break-all;">
                            <strong>ID:</strong> <code>{project.get('project_id', 'N/A')}</code>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Health Score", f"{health_score}/100")
                    st.progress(health_score / 100)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.caption(f"✅ {project.get('completion_rate', 0)}% done")
                    with col_b:
                        overdue = project.get('overdue_tasks', 0)
                        st.caption(f"⚠️ {overdue} overdue")
                    
                    # Issues
                    issues = project.get('critical_issues', [])
                    if issues:
                        with st.expander("⚠️ Issues"):
                            for issue in issues:
                                st.caption(f"• {issue}")
                    
                    # View details button
                    if st.button("📊 View Details", key=f"view_{project.get('project_id')}", width="stretch"):
                        st.session_state.current_project = project.get('project_id')
                        st.rerun()
    
    st.divider()
    
    # =========================
    # SECTION 5: Charts
    # =========================
    st.subheader("📈 Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Health Score Distribution**")
        
        if projects:
            # Prepare data
            df_health = pd.DataFrame([
                {
                    'Project': p.get('project_name', 'Unnamed')[:15],
                    'Health Score': p.get('health_score', 0),
                    'Status': p.get('health_status', 'UNKNOWN')
                }
                for p in projects[:10]
            ])
            
            # Color mapping
            color_map = {
                'CRITICAL': '#ef4444',
                'AT_RISK': '#f59e0b', 
                'GOOD': '#84cc16',
                'EXCELLENT': '#22c55e',
                'UNKNOWN': '#6b7280'
            }
            
            # Create figure with explicit colors
            fig = go.Figure()
            
            for _, row in df_health.iterrows():
                color = color_map.get(row['Status'], '#6b7280')
                fig.add_trace(go.Bar(
                    x=[row['Project']],
                    y=[row['Health Score']],
                    marker=dict(
                        color=color,
                        line=dict(color='rgba(255,255,255,0.3)',
                        width=2),
                        opacity=1.0
                    ),
                    text=[row['Health Score']],
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Arial Black'),
                    name=row['Status'],
                    showlegend=False,
                    hovertemplate=f"<b>{row['Project']}</b><br>Health: {row['Health Score']}/100<extra></extra>"
                ))
            
            # Dark theme layout
            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(31, 41, 55, 0.4)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                xaxis=dict(
                    title="",
                    tickangle=-45,
                    tickfont=dict(color='white', size=10),
                    showgrid=False,
                    showline=True,
                    linecolor='rgba(255,255,255,0.2)'
                ),
                yaxis=dict(
                    title="Health Score",
                    range=[0, 110],
                    tickfont=dict(color='white', size=10),
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    showline=False,
                    zeroline=True,
                    zerolinecolor='rgba(255,255,255,0.2)'
                ),
                margin=dict(l=50, r=20, t=20, b=100),
                bargap=0.3
            )
            
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No project data available")

    with col2:
        st.markdown("**Project Status Breakdown**")
        
        if projects:
            # Pie chart of status distribution
            status_counts = {
                'Healthy': agg.get('healthy_projects', 0),
                'At Risk': agg.get('at_risk_projects', 0),
                'Critical': agg.get('critical_projects', 0)
            }
            
            # Only show if there's data
            if sum(status_counts.values()) > 0:
                fig = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    color=list(status_counts.keys()),
                    color_discrete_map={
                        'Healthy': '#22c55e',
                        'At Risk': '#f59e0b',
                        'Critical': '#ef4444'
                    },
                    hole=0.4  # Donut chart
                )
                
                # Dark theme styling
                fig.update_layout(
                    height=350,
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=11),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1,
                        font=dict(color='white')
                    )
                )
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    textfont=dict(color='white', size=12, family='Arial Black'),
                    marker=dict(line=dict(color='rgba(255,255,255,0.3)', width=2))
                )
                
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No status data available")
        else:
            st.info("No project data")

    st.divider()

    # Resource heatmap (KEEPING THIS PART - just reformatted)
    overloaded_members = portfolio_data.get('resource_insights', {}).get('overloaded_members', [])

    if overloaded_members:
        st.markdown("**🔥 Resource Bottlenecks**")
        st.warning(f"**{len(overloaded_members)} team member(s) working across multiple projects:**")
        
        for member in overloaded_members:
            with st.expander(f"👤 {member['name']} - {member['project_count']} projects"):
                st.write(f"**Total Tasks:** {member['total_tasks']}")
                st.write(f"**Overdue:** {member['overdue_tasks']}")
                st.write(f"**Projects:** {', '.join(member['projects'])}")
                st.warning("💡 Consider redistributing tasks to balance workload")

# ============================================================================
# PAGE 1: AI CHATBOT 
# ============================================================================
elif page == "💬 AI Chatbot":
    st.title("💬 AI Project Assistant")
    st.markdown("Ask questions about your project and get instant answers!")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - Who are the team members?
            - What is the project status?
            - Show me overdue tasks
            - What tasks are in progress?
            """)
        with col2:
            st.markdown("""
            - What is John's workload?
            - List all technologies used
            - Show milestone details
            - Get user availability
            """)
    
    st.divider()
    
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
            with st.spinner("🤔 Thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/chat/{project_id}",
                        json={
                            "query": prompt,
                            "user_id": st.session_state.user_id
                        },
                        timeout=60
                    )
                    
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
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============================================================================
# PAGE 2: DASHBOARD
# ============================================================================

elif page == "📊 Dashboard":
    st.title("📊 Project Dashboard")
    
    # Refresh button
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🔄 Refresh", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    # Get data
    with st.spinner("Loading dashboard data..."):
        health_data = get_project_health(project_id)
        velocity_data = get_velocity(project_id, days=7)
    
    if "error" in health_data:
        st.error(f"❌ Error loading health data: {health_data['error']}")
        st.stop()
    
    # Header metrics
    st.subheader("Project Health Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        health_score = health_data.get('health_score', 0)
        st.metric(
            "Health Score",
            f"{health_score}/100",
            delta=None,
            help="Overall project health (0-100)"
        )
    
    with col2:
        status = health_data.get('health_status', 'UNKNOWN')
        emoji = health_data.get('status_emoji', '⚪')
        st.metric(
            "Status",
            f"{emoji} {status}",
            delta=None
        )
    
    with col3:
        metrics = health_data.get('metrics', {})
        completion_rate = metrics.get('completion_rate', 0)
        st.metric(
            "Completion Rate",
            f"{completion_rate}%",
            delta=f"{metrics.get('completed_tasks', 0)}/{metrics.get('total_tasks', 0)} tasks"
        )
    
    with col4:
        overdue = metrics.get('overdue_tasks', 0)
        st.metric(
            "Overdue Tasks",
            overdue,
            delta=f"-{overdue}" if overdue > 0 else "0",
            delta_color="inverse"
        )
    
    st.divider()
    
    # Health breakdown
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Health Score Breakdown")
        breakdown = health_data.get('breakdown', {})
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Health"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': health_data.get('status_color', 'gray')},
                'steps': [
                    {'range': [0, 40], 'color': "#fee2e2"},
                    {'range': [40, 60], 'color': "#fef3c7"},
                    {'range': [60, 80], 'color': "#dbeafe"},
                    {'range': [80, 100], 'color': "#dcfce7"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 60
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.subheader("Score Components")
        st.metric("Completion", f"{breakdown.get('completion_score', 0)}/40")
        st.metric("Timeline", f"{breakdown.get('timeline_score', 0)}/30")
        st.metric("Balance", f"{breakdown.get('balance_score', 0)}/20")
        st.metric("Velocity", f"{breakdown.get('velocity_score', 0)}/10")
    
    st.divider()
    
    # Task distribution and velocity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Task Distribution")
        task_data = pd.DataFrame({
            'Status': ['Completed', 'In Progress', 'Overdue'],
            'Count': [
                metrics.get('completed_tasks', 0),
                metrics.get('in_progress_tasks', 0),
                metrics.get('overdue_tasks', 0)
            ]
        })
        
        fig = px.pie(
            task_data,
            values='Count',
            names='Status',
            color='Status',
            color_discrete_map={
                'Completed': '#22c55e',
                'In Progress': '#3b82f6',
                'Overdue': '#ef4444'
            }
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.subheader("🚀 Team Velocity")
        if "error" not in velocity_data:
            st.metric(
                "Tasks Completed (7 days)",
                velocity_data.get('tasks_completed', 0),
                delta=f"{velocity_data.get('trend_emoji', '')} {velocity_data.get('trend', 'UNKNOWN')}"
            )
            st.metric(
                "Velocity",
                f"{velocity_data.get('velocity_per_day', 0):.1f} tasks/day"
            )
            st.metric(
                "Team Size",
                velocity_data.get('team_size', 0)
            )
        else:
            st.error("Unable to load velocity data")

# ============================================================================
# PAGE 3: ANALYTICS
# ============================================================================

elif page == "🔍 Analytics":
    st.title("🔍 Deep Analytics")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Workload",
        "🚧 Bottlenecks",
        "🎯 Milestones",
        "📈 Velocity"
    ])
    
    # TAB 1: Workload Analysis
    with tab1:
        st.subheader("Team Workload Distribution")
        
        workload_data = get_workload_analysis(project_id)
        
        if "error" in workload_data:
            st.error(f"Error: {workload_data['error']}")
        else:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Team Size", workload_data.get('team_size', 0))
            with col2:
                st.metric("Balance Status", workload_data.get('balance_status', 'UNKNOWN'))
            with col3:
                stats = workload_data.get('statistics', {})
                st.metric("Avg Tasks/Person", f"{stats.get('average_tasks_per_person', 0):.1f}")
            with col4:
                st.metric("Active Tasks", stats.get('total_active_tasks', 0))
            
            st.divider()
            
            # Workload chart
            all_members = workload_data.get('all_members', [])
            if all_members:
                df = pd.DataFrame([
                    {
                        'Name': m['user_name'],
                        'Total Tasks': m['total_tasks'],
                        'Overdue': m['overdue_tasks']
                    }
                    for m in all_members
                ])
                
                fig = px.bar(
                    df,
                    x='Name',
                    y=['Total Tasks', 'Overdue'],
                    title="Workload per Team Member",
                    barmode='group'
                )
                st.plotly_chart(fig, width="stretch")
                
                # Detailed breakdown
                st.subheader("Team Member Details")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("##### 🔴 Overloaded")
                    overloaded = workload_data.get('overloaded_members', [])
                    if overloaded:
                        for m in overloaded:
                            st.warning(f"**{m['user_name']}**: {m['total_tasks']} tasks")
                    else:
                        st.success("No overloaded members")
                
                with col2:
                    st.markdown("##### 🟢 Balanced")
                    balanced = workload_data.get('balanced_members', [])
                    st.info(f"{len(balanced)} members with balanced workload")
                
                with col3:
                    st.markdown("##### 🔵 Available")
                    underutilized = workload_data.get('underutilized_members', [])
                    if underutilized:
                        for m in underutilized:
                            st.info(f"**{m['user_name']}**: {m['total_tasks']} tasks")
                    else:
                        st.info("All members are active")
    
    # TAB 2: Bottlenecks
    with tab2:
        st.subheader("Project Bottlenecks & Blockers")
        
        bottleneck_data = get_bottlenecks(project_id)
        
        if "error" in bottleneck_data:
            st.error(f"Error: {bottleneck_data['error']}")
        else:
            severity = bottleneck_data.get('severity', 'UNKNOWN')
            
            # Severity indicator
            if severity == 'CRITICAL':
                st.error(f"🔴 Bottleneck Severity: **{severity}**")
            elif severity == 'HIGH':
                st.warning(f"🟠 Bottleneck Severity: **{severity}**")
            elif severity == 'MEDIUM':
                st.info(f"🟡 Bottleneck Severity: **{severity}**")
            else:
                st.success(f"🟢 Bottleneck Severity: **{severity}**")
            
            summary = bottleneck_data.get('summary', {})
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Critical Users", summary.get('critical_users_count', 0))
            with col2:
                st.metric("Long Overdue", summary.get('long_overdue_count', 0))
            with col3:
                st.metric("Blocked High Priority", summary.get('blocked_high_priority', 0))
            with col4:
                st.metric("At-Risk Milestones", summary.get('at_risk_milestones', 0))
            
            st.divider()
            
            bottlenecks = bottleneck_data.get('bottlenecks', {})
            
            # Critical Users
            critical_users = bottlenecks.get('critical_users', [])
            if critical_users:
                st.subheader("🚨 Critical Users (Overloaded)")
                for user in critical_users:
                    with st.expander(f"{user['user_name']} - {user['overdue_count']} overdue tasks"):
                        for task in user['overdue_tasks'][:5]:
                            st.write(f"- **{task['task_name']}** ({task['days_overdue']} days overdue)")
            
            # Long Overdue Tasks
            long_overdue = bottlenecks.get('long_overdue_tasks', [])
            if long_overdue:
                st.subheader("⏰ Long Overdue Tasks (>14 days)")
                for task in long_overdue[:5]:
                    st.warning(f"**{task['task_name']}** - {task['days_overdue']} days overdue")
    
    # TAB 3: Milestone Risks
    with tab3:
        st.subheader("Milestone Risk Analysis")
        
        milestone_data = get_milestone_risks(project_id)
        
        if "error" in milestone_data:
            st.error(f"Error: {milestone_data['error']}")
        elif milestone_data.get('milestones'):
            risk_summary = milestone_data.get('risk_summary', {})
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔴 Critical", risk_summary.get('CRITICAL', 0))
            with col2:
                st.metric("🟠 High", risk_summary.get('HIGH', 0))
            with col3:
                st.metric("🟡 Medium", risk_summary.get('MEDIUM', 0))
            with col4:
                st.metric("🟢 Low", risk_summary.get('LOW', 0))
            
            st.divider()
            
            # Milestone details
            for milestone in milestone_data['milestones']:
                risk_level = milestone['risk_level']
                
                if risk_level == 'CRITICAL':
                    color = 'error'
                elif risk_level == 'HIGH':
                    color = 'warning'
                elif risk_level == 'MEDIUM':
                    color = 'info'
                else:
                    color = 'success'
                
                with st.expander(f"{milestone['milestone_title']} - {risk_level}", expanded=(risk_level in ['CRITICAL', 'HIGH'])):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Completion", f"{milestone['completion_percentage']}%")
                    with col2:
                        st.metric("Days Remaining", milestone.get('days_remaining', 'N/A'))
                    with col3:
                        st.metric("Overdue Tasks", milestone['overdue_tasks'])
                    
                    if milestone.get('risk_factors'):
                        st.markdown("**Risk Factors:**")
                        for factor in milestone['risk_factors']:
                            st.write(f"- {factor}")
        else:
            st.info("No active milestones found")
    
    # TAB 4: Velocity Trends
    with tab4:
        st.subheader("Team Velocity Analysis")
        
        # Time period selector
        days = st.selectbox("Select Time Period", [7, 14, 30], index=0)
        
        velocity_data = get_velocity(project_id, days=days)
        
        if "error" not in velocity_data:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    f"Tasks Completed ({days} days)",
                    velocity_data.get('tasks_completed', 0)
                )
            with col2:
                st.metric(
                    "Daily Velocity",
                    f"{velocity_data.get('velocity_per_day', 0):.2f} tasks/day"
                )
            with col3:
                st.metric(
                    "Per Person",
                    f"{velocity_data.get('velocity_per_person_per_day', 0):.2f} tasks/day"
                )
            
            st.divider()
            
            # Trend visualization
            trend = velocity_data.get('trend', 'STEADY')
            trend_pct = velocity_data.get('trend_percentage', 0)
            
            if trend == 'ACCELERATING':
                st.success(f"📈 Trend: **{trend}** (+{trend_pct:.1f}%)")
                st.info("Team velocity is improving! Productivity is increasing.")
            elif trend == 'SLOWING':
                st.warning(f"📉 Trend: **{trend}** ({trend_pct:.1f}%)")
                st.warning("Team velocity is decreasing. Consider investigating bottlenecks.")
            else:
                st.info(f"➡️ Trend: **{trend}** ({trend_pct:+.1f}%)")
                st.info("Team velocity is stable.")

# ============================================================================
# PAGE 4: REPORTS
# ============================================================================

elif page == "📄 Reports":
    st.title("📄 Generated Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Daily", "Weekly", "Executive", "Team", "Risks"],
        format_func=lambda x: f"📄 {x} Report"
    )
    
    if st.button("📥 Generate Report", type="primary", width="stretch"):
        with st.spinner(f"Generating {report_type.lower()} report..."):
            report_data = get_report(project_id, report_type.lower())
            
            if "error" in report_data:
                st.error(f"Error: {report_data['error']}")
            else:
                st.success("✅ Report generated successfully!")
                
                # Display report
                st.markdown("---")
                st.code(report_data.get('report', 'No report content'), language=None)
                
                # Download button
                st.download_button(
                    label="📥 Download Report",
                    data=report_data.get('report', ''),
                    file_name=f"{report_type.lower()}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    width="stretch"
                )

# ============================================================================
# PAGE 5: RECOMMENDATIONS
# ============================================================================

elif page == "💡 Recommendations":
    st.title("💡 AI-Powered Recommendations")
    st.markdown("Get intelligent, actionable recommendations to improve your project health.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("🤖 Using AI-Powered Recommendations (Gemini)")
        method = "ai"

    with col2:
        if st.button("🔄 Refresh", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    with st.spinner("Generating recommendations..."):
        rec_data = get_recommendations(project_id, method=method)
    
    if "error" in rec_data:
        st.error(f"Error: {rec_data['error']}")
    else:
        st.success(f"✅ Generated {rec_data.get('total', 0)} recommendations using **{rec_data.get('method', 'unknown')}** method")
        
        recommendations = rec_data.get('recommendations', [])
        
        if recommendations:
            # Filter by priority
            priority_filter = st.multiselect(
                "Filter by Priority",
                ["HIGH", "MEDIUM", "LOW"],
                default=["HIGH", "MEDIUM", "LOW"]
            )
            
            filtered_recs = [r for r in recommendations if r.get('priority') in priority_filter]
            
            st.markdown(f"### Showing {len(filtered_recs)} recommendations")
            
            for i, rec in enumerate(filtered_recs, 1):
                priority = rec.get('priority', 'UNKNOWN')
                
                # Style based on priority
                if priority == 'HIGH':
                    container_class = "recommendation-high"
                    emoji = "🔴"
                elif priority == 'MEDIUM':
                    container_class = "recommendation-medium"
                    emoji = "🟡"
                else:
                    container_class = "recommendation-low"
                    emoji = "🟢"
                
                with st.container():
                    st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
                    
                    st.markdown(f"### {emoji} #{i} - {priority} Priority")
                    st.markdown(f"**Category:** {rec.get('category', 'Unknown')}")
                    st.markdown(f"**Action:** {rec.get('action', 'No action specified')}")
                    st.markdown(f"**Reason:** {rec.get('reason', 'No reason provided')}")
                    st.markdown(f"**Expected Impact:** {rec.get('expected_impact', 'Unknown')}")
                    st.markdown(f"**Effort Required:** {rec.get('effort', 'Unknown')}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")
        else:
            st.info("No recommendations available at this time.")

# Footer
st.markdown("---")
st.caption(f"Project Management AI System v2.0 | Connected to: {API_URL}")