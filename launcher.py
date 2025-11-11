# This script launches two independent services (FastAPI and Streamlit)
# and monitors them, ensuring a clean shutdown if either fails.

import subprocess
import time
import sys
import requests
import os
import signal

# Check if the PORT env variable exists (standard for deployment platforms)
IS_PRODUCTION = bool(os.environ.get('PORT'))
# Streamlit MUST use the public PORT for the platform to detect the service
STREAMLIT_PORT = os.environ.get('PORT', '8501')
# FastAPI runs on a fixed internal port (private to the container)
FASTAPI_PORT = '8000'
# Listen on all interfaces (0.0.0.0) in production for external access
HOST = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'

# Global process references
fastapi_process = None
streamlit_process = None

def check_fastapi_ready(max_attempts=30):
    """Wait for FastAPI to be ready using an internal health check."""
    print("⏳ Waiting for FastAPI to start...", flush=True)
    health_url = f"http://127.0.0.1:{FASTAPI_PORT}/health"
    
    for i in range(max_attempts):
        # 1. Check if the process died before being ready
        if fastapi_process and fastapi_process.poll() is not None:
            print(f"❌ FastAPI process died with exit code: {fastapi_process.poll()}", flush=True)
            print("🛑 Check logs for ModuleNotFoundError or configuration errors.", flush=True)
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
            
    return False

def cleanup_processes(signum=None, frame=None):
    """Clean shutdown of all processes upon termination signals."""
    global fastapi_process, streamlit_process
    
    print("\n\n🛑 Shutting down services...", flush=True)
    
    # 1. Terminate Streamlit
    if streamlit_process:
        print("⏳ Stopping Streamlit...", flush=True)
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()
    
    # 2. Terminate FastAPI
    if fastapi_process:
        print("⏳ Stopping FastAPI...", flush=True)
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            fastapi_process.kill()
    
    print("✅ All services stopped", flush=True)
    if signum is not None:
        sys.exit(0)

def main():
    global fastapi_process, streamlit_process
    
    env_name = "PRODUCTION" if IS_PRODUCTION else "DEVELOPMENT"
    print(f"🚀 Starting Project Chatbot System ({env_name} mode)...\n", flush=True)
    
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
    
    if not IS_PRODUCTION:
        fastapi_cmd.append("--reload")
    
    # Popen ensures the subprocess logs go directly to the main console
    fastapi_process = subprocess.Popen(fastapi_cmd)
    
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
    
    if IS_PRODUCTION:
        # These flags are essential for cloud deployment
        streamlit_cmd.extend([
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    
    streamlit_process = subprocess.Popen(streamlit_cmd)
    
    # --- 4. Monitor Processes ---
    print(f"✅ Services are running. Monitoring processes...", flush=True)
    try:
        while True:
            time.sleep(1)
            
            # Check if either process has terminated unexpectedly
            if fastapi_process.poll() is not None or streamlit_process.poll() is not None:
                print("\n❌ One service failed. Initiating full shutdown.", flush=True)
                cleanup_processes()
                break
            
    except KeyboardInterrupt:
        cleanup_processes()

if __name__ == "__main__":
    main()