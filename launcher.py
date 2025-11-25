# launcher.py
# This script launches two independent services (FastAPI and Streamlit)
# and monitors them, ensuring a clean shutdown if either fails.

import subprocess
import time
import sys
import requests
import os
import signal

from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Check if the PORT env variable exists (standard for deployment platforms)
IS_PRODUCTION = bool(os.environ.get('PORT'))

# Streamlit MUST use the public PORT for the platform to detect the service
STREAMLIT_PORT = os.environ.get('PORT', '8501')

# FastAPI runs on a fixed internal port (private to the container)
FASTAPI_PORT = '8000'

# Listen on all interfaces (0.0.0.0) in production for external access
HOST = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'

# Set the FastAPI URL that Streamlit will use to connect
FASTAPI_URL = f"http://127.0.0.1:{FASTAPI_PORT}"

# Global process references
fastapi_process = None
streamlit_process = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_fastapi_ready(max_attempts=30):
    """Wait for FastAPI to be ready using an internal health check."""
    print("⏳ Waiting for FastAPI to start...", flush=True)
    health_url = f"{FASTAPI_URL}/health"
    
    for i in range(max_attempts):
        # 1. Check if the process died before being ready
        if fastapi_process and fastapi_process.poll() is not None:
            print(f"❌ FastAPI process died with exit code: {fastapi_process.poll()}", flush=True)
            print("🛑 Check logs for ModuleNotFoundError or configuration errors.", flush=True)
            print("   Common issues:", flush=True)
            print("   - Missing dependencies (pip install -r requirements.txt)", flush=True)
            print("   - MongoDB connection failure (check MONGO_URI)", flush=True)
            print("   - Missing environment variables (GOOGLE_API_KEY)", flush=True)
            return False
            
        # 2. Try to connect to the health endpoint
        try:
            response = requests.get(health_url, timeout=1)
            if response.status_code == 200:
                print("✅ FastAPI is ready!", flush=True)
                return True
        except requests.exceptions.RequestException:
            pass # Keep trying if connection fails
        
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   Still waiting... ({i+1}/{max_attempts})", flush=True)
    
    print(f"❌ FastAPI failed to respond after {max_attempts} seconds", flush=True)
    return False

def cleanup_processes(signum=None, frame=None):
    """Clean shutdown of all processes upon termination signals."""
    global fastapi_process, streamlit_process
    
    print("\n\n🛑 Shutting down services...", flush=True)
    
    # 1. Terminate Streamlit first (frontend should stop before backend)
    if streamlit_process:
        print("⏳ Stopping Streamlit...", flush=True)
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
            print("✅ Streamlit stopped", flush=True)
        except subprocess.TimeoutExpired:
            print("⚠️  Force killing Streamlit...", flush=True)
            streamlit_process.kill()
    
    # 2. Terminate FastAPI
    if fastapi_process:
        print("⏳ Stopping FastAPI...", flush=True)
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=5)
            print("✅ FastAPI stopped", flush=True)
        except subprocess.TimeoutExpired:
            print("⚠️  Force killing FastAPI...", flush=True)
            fastapi_process.kill()
    
    print("✅ All services stopped cleanly", flush=True)
    if signum is not None:
        sys.exit(0)

# ============================================================================
# MAIN LAUNCHER
# ============================================================================

def main():
    global fastapi_process, streamlit_process
    
    env_name = "PRODUCTION" if IS_PRODUCTION else "DEVELOPMENT"
    print("="*70, flush=True)
    print(f"🚀 Project Management Intelligent System - {env_name} Mode", flush=True)
    print("="*70, flush=True)
    
    # Display configuration
    print(f"\n📋 Configuration:", flush=True)
    print(f"   Mode: {env_name}", flush=True)
    print(f"   Host: {HOST}", flush=True)
    print(f"   Streamlit Port: {STREAMLIT_PORT}", flush=True)
    print(f"   FastAPI Port: {FASTAPI_PORT}", flush=True)
    print(f"   FastAPI URL: {FASTAPI_URL}", flush=True)
    print(f"   MongoDB URI: {'Set ✅' if os.getenv('MONGO_URI') else 'Missing ❌'}", flush=True)
    print(f"   Google API Key: {'Set ✅' if os.getenv('GOOGLE_API_KEY') else 'Missing ❌'}", flush=True)
    print(f"\n{'='*70}\n", flush=True)
    
    # Verify required environment variables
    if not os.getenv('MONGO_URI'):
        print("❌ ERROR: MONGO_URI environment variable not set!", flush=True)
        print("   Set it in your .env file or deployment environment", flush=True)
        sys.exit(1)
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  WARNING: GOOGLE_API_KEY not set. AI features may not work.", flush=True)
    
    # Set up signal handlers for graceful shutdown (e.g., when the platform kills the process)
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)
    
    # --- 1. Start FastAPI (Backend) ---
    print(f"📡 Starting FastAPI backend on {HOST}:{FASTAPI_PORT}...", flush=True)
    
    fastapi_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", HOST,
        "--port", FASTAPI_PORT
    ]
    
    # Add reload only in development
    if not IS_PRODUCTION:
        fastapi_cmd.append("--reload")
        print("   (Hot reload enabled)", flush=True)
    
    # Start FastAPI process
    # Popen ensures the subprocess logs go directly to the main console
    try:
        fastapi_process = subprocess.Popen(
            fastapi_cmd,
            env={**os.environ}  # Pass all environment variables
        )
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}", flush=True)
        sys.exit(1)
    
    # --- 2. Wait for FastAPI to be ready ---
    if not check_fastapi_ready():
        print("\n❌ FastAPI failed to start. Exiting.", flush=True)
        cleanup_processes()
        return
    
    # --- 3. Start Streamlit (Frontend) ---
    print(f"\n🎨 Starting Streamlit interface on port {STREAMLIT_PORT}...", flush=True)
    
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", STREAMLIT_PORT,
        "--server.address", HOST,
    ]
    
    # Production-specific flags
    if IS_PRODUCTION:
        streamlit_cmd.extend([
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
        print("   (Production mode: headless, CORS disabled)", flush=True)
    
    # Create environment with FASTAPI_URL set
    streamlit_env = os.environ.copy()
    streamlit_env['FASTAPI_URL'] = FASTAPI_URL
    
    try:
        streamlit_process = subprocess.Popen(
            streamlit_cmd,
            env=streamlit_env  # Pass FASTAPI_URL to Streamlit
        )
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}", flush=True)
        cleanup_processes()
        return
    
    # Give Streamlit a moment to start
    time.sleep(3)
    
    # --- 4. Final Status Check ---
    if streamlit_process.poll() is not None:
        print("❌ Streamlit failed to start", flush=True)
        cleanup_processes()
        return
    
    # --- 5. Success! ---
    print("\n" + "="*70, flush=True)
    print("✅ All services started successfully!", flush=True)
    print("="*70, flush=True)
    
    if IS_PRODUCTION:
        print(f"\n🌐 Application available at: http://0.0.0.0:{STREAMLIT_PORT}", flush=True)
        print(f"📡 API available at: http://0.0.0.0:{FASTAPI_PORT}", flush=True)
    else:
        print(f"\n🌐 Streamlit UI: http://localhost:{STREAMLIT_PORT}", flush=True)
        print(f"📡 FastAPI docs: http://localhost:{FASTAPI_PORT}/docs", flush=True)
        print(f"📊 Health check: http://localhost:{FASTAPI_PORT}/health", flush=True)
    
    print(f"\n💡 Tip: Press Ctrl+C to stop all services", flush=True)
    print("="*70 + "\n", flush=True)
    
    # --- 6. Monitor Processes ---
    print("🔍 Monitoring processes...\n", flush=True)
    
    failure_count = 0
    try:
        while True:
            time.sleep(2)  # Check every 2 seconds
            
            # Check FastAPI
            if fastapi_process.poll() is not None:
                exit_code = fastapi_process.poll()
                print(f"\n❌ FastAPI terminated unexpectedly (exit code: {exit_code})", flush=True)
                failure_count += 1
                break
            
            # Check Streamlit
            if streamlit_process.poll() is not None:
                exit_code = streamlit_process.poll()
                print(f"\n❌ Streamlit terminated unexpectedly (exit code: {exit_code})", flush=True)
                failure_count += 1
                break
    
            
    except KeyboardInterrupt:
        print("\n⌨️  Keyboard interrupt received", flush=True)
    
    # Cleanup on failure or interrupt
    cleanup_processes()
    
    # Exit with appropriate code
    if failure_count > 0:
        sys.exit(1)  # Exit with error code
    else:
        sys.exit(0)  # Clean exit

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()