import subprocess
import time
import sys
import requests
import os
import signal

# --- Configuration ---
# Detect environment
IS_PRODUCTION = bool(os.environ.get('PORT'))
# Streamlit must run on the public port
STREAMLIT_PORT = os.environ.get('PORT', '8501')
# FastAPI runs on a fixed internal port
FASTAPI_PORT = '8000'
# Use 0.0.0.0 in production, otherwise localhost for local testing
HOST = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'

# Global process references
fastapi_process = None
streamlit_process = None

def check_fastapi_ready(max_attempts=30):
    """Wait for FastAPI to be ready using a health check."""
    print("⏳ Waiting for FastAPI to start...", flush=True)
    # Always check the internal endpoint on 127.0.0.1
    health_url = f"http://127.0.0.1:{FASTAPI_PORT}/health"
    
    for i in range(max_attempts):
        if fastapi_process and fastapi_process.poll() is not None:
            # Check if process died
            print(f"❌ FastAPI process died with exit code: {fastapi_process.poll()}", flush=True)
            print("Please check logs above for FastAPI startup errors.", flush=True)
            return False
            
        try:
            # Use a short timeout for the check
            response = requests.get(health_url, timeout=1)
            if response.status_code == 200:
                print("✅ FastAPI is ready!", flush=True)
                return True
        except requests.exceptions.RequestException:
            # Ignore connection errors while waiting
            pass
        
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   Still waiting... ({i+1}/{max_attempts})", flush=True)
            
    return False

def cleanup_processes(signum=None, frame=None):
    """Clean shutdown of all processes upon termination signals."""
    global fastapi_process, streamlit_process
    
    print("\n\n🛑 Shutting down services...", flush=True)
    
    # Terminate Streamlit
    if streamlit_process:
        print("⏳ Stopping Streamlit...", flush=True)
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()
    
    # Terminate FastAPI
    if fastapi_process:
        print("⏳ Stopping FastAPI...", flush=True)
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            fastapi_process.kill()
    
    print("✅ All services stopped", flush=True)
    # Only exit if called by signal handler
    if signum is not None:
        sys.exit(0)

def main():
    global fastapi_process, streamlit_process
    
    env_name = "PRODUCTION" if IS_PRODUCTION else "DEVELOPMENT"
    print(f"🚀 Starting Project Chatbot System ({env_name} mode)...\n", flush=True)
    
    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)
    
    # --- 1. Start FastAPI ---
    print(f"📡 Starting FastAPI backend on {HOST}:{FASTAPI_PORT}...", flush=True)
    
    fastapi_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", HOST,
        "--port", FASTAPI_PORT
    ]
    
    if not IS_PRODUCTION:
        fastapi_cmd.append("--reload")
    
    # By using stdout=None and stderr=None (default behavior), 
    # the subprocess output goes directly to the main process's stdout/stderr, 
    # which the deployment platform can reliably capture.
    fastapi_process = subprocess.Popen(fastapi_cmd)
    
    # Give it a moment to initialize the command
    time.sleep(1)
    
    # --- 2. Wait for FastAPI ---
    if not check_fastapi_ready():
        print("\n❌ FastAPI failed to start. Shutting down.", flush=True)
        cleanup_processes()
        return
    
    # --- 3. Start Streamlit ---
    print(f"\n🎨 Starting Streamlit interface on port {STREAMLIT_PORT}...", flush=True)
    
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", STREAMLIT_PORT,
        "--server.address", HOST
    ]
    
    if IS_PRODUCTION:
        # Essential flags for containerized Streamlit
        streamlit_cmd.extend([
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    
    # Let Streamlit also inherit the parent's I/O streams
    streamlit_process = subprocess.Popen(streamlit_cmd)
    
    # --- 4. Monitor Processes ---
    print(f"✅ Services are running. Monitoring processes...", flush=True)
    try:
        while True:
            time.sleep(1)
            
            # Check for FastAPI failure
            if fastapi_process.poll() is not None:
                print(f"\n❌ FastAPI has stopped! Exit Code: {fastapi_process.poll()}", flush=True)
                cleanup_processes()
                break
            
            # Check for Streamlit failure (which means the main web service failed)
            if streamlit_process.poll() is not None:
                print(f"\n❌ Streamlit has stopped! Exit Code: {streamlit_process.poll()}", flush=True)
                cleanup_processes()
                break
            
    except KeyboardInterrupt:
        cleanup_processes()

if __name__ == "__main__":
    main()