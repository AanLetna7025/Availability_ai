# streamlit_app.py

import streamlit as st
import requests
import uuid
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime



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

# Check API connection
@st.cache_data(ttl=60)
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if not check_api_health():
    st.error("❌ Cannot connect to backend API. Make sure FastAPI is running on port 8000.")
    st.stop()

# ============================================================================
# SIDEBAR - PROJECT SELECTION & NAVIGATION
# ============================================================================
with st.sidebar:
    st.image("https://cdn3d.iconscout.com/3d/premium/thumb/ai-robot-character-standing-at-attention-with-smiling-face-3d-icon-png-download-11431326.png", width=80)
    st.title(" Navigation")
    
    # Project ID input
    project_id = st.text_input(
        "Project ID",
        value=st.session_state.current_project,
        placeholder="Enter project ID...",
        help="Enter your MongoDB project ObjectId"
    )
    
    if project_id != st.session_state.current_project:
        st.session_state.current_project = project_id
        if project_id not in st.session_state.messages:
            st.session_state.messages[project_id] = []
    
    st.divider()
    
    # Page navigation
    page = st.radio(
        "Select Page",
        [
            "💬 AI Chatbot",
            "📊 Dashboard",
            "🔍 Analytics",
            "📄 Reports",
            "💡 Recommendations"
        ],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # User info
    st.caption(f"👤 User: `{st.session_state.user_id[:8]}...`")
    st.caption(f"🔗 API: `{API_URL}`")
    
    # Clear chat button (only show on chatbot page)
    if page == "💬 AI Chatbot":
        if st.button("🗑️ Clear Chat", use_container_width=True):
            if project_id in st.session_state.messages:
                st.session_state.messages[project_id] = []
                st.rerun()

# Require project ID for all pages
if not project_id:
    st.info("👈 Please enter a Project ID in the sidebar to continue")
    st.stop()

# ============================================================================
# HELPER FUNCTIONS FOR API CALLS
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_project_health(proj_id):
    try:
        response = requests.get(f"{API_URL}/api/projects/{proj_id}/health", timeout=10)
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
# PAGE 1: AI CHATBOT (Your existing chatbot)
# ============================================================================

if page == "💬 AI Chatbot":
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
        if st.button("🔄 Refresh", use_container_width=True):
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
        st.plotly_chart(fig, use_container_width=True)
    
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
        st.plotly_chart(fig, use_container_width=True)
    
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
                st.plotly_chart(fig, use_container_width=True)
                
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
    
    if st.button("📥 Generate Report", type="primary", use_container_width=True):
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
                    use_container_width=True
                )

# ============================================================================
# PAGE 5: RECOMMENDATIONS
# ============================================================================

elif page == "💡 Recommendations":
    st.title("💡 AI-Powered Recommendations")
    st.markdown("Get intelligent, actionable recommendations to improve your project health.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        method = st.radio(
            "Select Method",
            ["ai", "rules"],
            format_func=lambda x: "🤖 AI-Powered (Gemini)" if x == "ai" else "⚡ Rule-Based (Fast)",
            horizontal=True
        )
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
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