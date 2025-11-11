import subprocess
import time
import sys
import requests
import os
import signal
import threading

# Global process references
fastapi_process = None
streamlit_process = None

# Detect environment
IS_PRODUCTION = bool(os.environ.get('PORT'))
STREAMLIT_PORT = os.environ.get('PORT', '8501')
FASTAPI_PORT = '8000'
HOST = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'

def log_process_output(process, name):
    """Log output from a process in real-time"""
    if process.stdout:
        for line in iter(process.stdout.readline, b''):
            if line:
                print(f"[{name}] {line.decode().strip()}", flush=True)
    if process.stderr:
        for line in iter(process.stderr.readline, b''):
            if line:
                print(f"[{name} ERROR] {line.decode().strip()}", flush=True)

def check_fastapi_ready(max_attempts=30):  # Increased timeout
    """Wait for FastAPI to be ready"""
    print("⏳ Waiting for FastAPI to start...", flush=True)
    health_url = f"http://127.0.0.1:{FASTAPI_PORT}/health"
    
    for i in range(max_attempts):
        # Check if process died
        if fastapi_process and fastapi_process.poll() is not None:
            print(f"❌ FastAPI process died with exit code: {fastapi_process.poll()}", flush=True)
            return False
            
        try:
            response = requests.get(health_url, timeout=2)
            if response.status_code == 200:
                print("✅ FastAPI is ready!", flush=True)
                return True
        except Exception as e:
            pass
        time.sleep(1)
        if i % 3 == 0:
            print(f"   Still waiting... ({i+1}/{max_attempts})", flush=True)
    return False

def cleanup_processes(signum=None, frame=None):
    """Clean shutdown of all processes"""
    global fastapi_process, streamlit_process
    
    print("\n\n🛑 Shutting down services...", flush=True)
    
    if streamlit_process:
        print("⏳ Stopping Streamlit...", flush=True)
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except:
            streamlit_process.kill()
    
    if fastapi_process:
        print("⏳ Stopping FastAPI...", flush=True)
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=5)
        except:
            fastapi_process.kill()
    
    print("✅ All services stopped", flush=True)
    sys.exit(0)

def main():
    global fastapi_process, streamlit_process
    
    env_name = "PRODUCTION" if IS_PRODUCTION else "DEVELOPMENT"
    print(f"🚀 Starting Project Chatbot System ({env_name} mode)...\n", flush=True)
    
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)
    
    # Start FastAPI
    print(f"📡 Starting FastAPI backend on {HOST}:{FASTAPI_PORT}...", flush=True)
    
    fastapi_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", HOST,
        "--port", FASTAPI_PORT
    ]
    
    if not IS_PRODUCTION:
        fastapi_cmd.append("--reload")
    
    if os.name == 'nt' and not IS_PRODUCTION:
        fastapi_process = subprocess.Popen(
            fastapi_cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # IMPORTANT: Capture both stdout and stderr separately
        fastapi_process = subprocess.Popen(
            fastapi_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0  # Unbuffered
        )
        
        # Start logging threads
        stdout_thread = threading.Thread(
            target=log_process_output, 
            args=(fastapi_process, "FastAPI"),
            daemon=True
        )
        stdout_thread.start()
    
    # Give it a moment to start
    time.sleep(3)
    
    # Wait for FastAPI
    if not check_fastapi_ready():
        print("\n❌ FastAPI failed to start!", flush=True)
        print("📋 Check the error messages above for details", flush=True)
        
        # Try to get any remaining output
        if fastapi_process.poll() is not None:
            try:
                stdout, stderr = fastapi_process.communicate(timeout=2)
                if stdout:
                    print(f"\n[FastAPI STDOUT]\n{stdout.decode()}", flush=True)
                if stderr:
                    print(f"\n[FastAPI STDERR]\n{stderr.decode()}", flush=True)
            except:
                pass
        
        cleanup_processes()
        return
    
    # Start Streamlit
    print(f"\n🎨 Starting Streamlit interface on port {STREAMLIT_PORT}...", flush=True)
    
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", STREAMLIT_PORT,
        "--server.address", HOST
    ]
    
    if IS_PRODUCTION:
        streamlit_cmd.extend([
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    
    try:
        streamlit_process = subprocess.Popen(streamlit_cmd)
        
        # Monitor processes
        while True:
            time.sleep(1)
            
            if fastapi_process.poll() is not None:
                print("\n❌ FastAPI has stopped!", flush=True)
                cleanup_processes()
                break
            
            if streamlit_process.poll() is not None:
                print("\n❌ Streamlit has stopped!", flush=True)
                cleanup_processes()
                break
                
    except KeyboardInterrupt:
        cleanup_processes()

if __name__ == "__main__":
    main()