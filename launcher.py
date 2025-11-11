import subprocess
import time
import sys
import requests
import os
import signal

# Global process references
fastapi_process = None
streamlit_process = None

# Detect environment
IS_PRODUCTION = os.environ.get('RENDER') or os.environ.get('PRODUCTION')
STREAMLIT_PORT = os.environ.get('PORT', '8501')  # Render provides PORT
FASTAPI_PORT = '8000'
HOST = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'

def check_fastapi_ready(max_attempts=15):
    """Wait for FastAPI to be ready"""
    print("⏳ Waiting for FastAPI to start...")
    health_url = f"http://{HOST}:{FASTAPI_PORT}/health"
    
    for i in range(max_attempts):
        try:
            response = requests.get(health_url, timeout=2)
            if response.status_code == 200:
                print("✅ FastAPI is ready!")
                return True
        except Exception as e:
            pass
        time.sleep(1)
        if i % 3 == 0:
            print(f"   Still waiting... ({i+1}/{max_attempts})")
    return False

def cleanup_processes(signum=None, frame=None):
    """Clean shutdown of all processes"""
    global fastapi_process, streamlit_process
    
    print("\n\n🛑 Shutting down services...")
    
    if streamlit_process:
        print("⏳ Stopping Streamlit...")
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except:
            streamlit_process.kill()
    
    if fastapi_process:
        print("⏳ Stopping FastAPI...")
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=5)
        except:
            fastapi_process.kill()
    
    print("✅ All services stopped")
    sys.exit(0)

def main():
    global fastapi_process, streamlit_process
    
    env_name = "PRODUCTION" if IS_PRODUCTION else "DEVELOPMENT"
    print(f"🚀 Starting Project Chatbot System ({env_name} mode)...\n")
    
    # Set up signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)
    
    # Check if FastAPI is already running (development mode)
    if not IS_PRODUCTION:
        try:
            response = requests.get(f"http://{HOST}:{FASTAPI_PORT}/health", timeout=1)
            if response.status_code == 200:
                print("✅ FastAPI is already running!")
                print("\n🎨 Starting Streamlit interface...")
                streamlit_process = subprocess.Popen(
                    [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"]
                )
                try:
                    streamlit_process.wait()
                except KeyboardInterrupt:
                    cleanup_processes()
                return
        except:
            pass
    
    # Start FastAPI in background
    print(f"📡 Starting FastAPI backend on {HOST}:{FASTAPI_PORT}...")
    
    fastapi_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", HOST,
        "--port", FASTAPI_PORT
    ]
    
    # Add --reload only in development
    if not IS_PRODUCTION:
        fastapi_cmd.append("--reload")
    
    if os.name == 'nt' and not IS_PRODUCTION:  # Windows development
        fastapi_process = subprocess.Popen(
            fastapi_cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:  # Linux/Mac or Production
        fastapi_process = subprocess.Popen(
            fastapi_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Wait for FastAPI to be ready
    if not check_fastapi_ready():
        print("\n❌ FastAPI failed to start!")
        if not IS_PRODUCTION:
            print("\n🔍 Please check the FastAPI terminal window for errors")
            print("💡 Try running manually in a separate terminal:")
            print(f"   uvicorn main:app --reload --port {FASTAPI_PORT}")
            input("\nPress Enter to exit...")
        cleanup_processes()
        return
    
    # Start Streamlit
    print(f"\n🎨 Starting Streamlit interface on port {STREAMLIT_PORT}...")
    print("="*60)
    
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", STREAMLIT_PORT,
        "--server.address", HOST
    ]
    
    # Add headless mode for production
    if IS_PRODUCTION:
        streamlit_cmd.extend([
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    
    if not IS_PRODUCTION:
        print("💡 Press Ctrl+C to stop both services")
        print("="*60)
    
    try:
        streamlit_process = subprocess.Popen(streamlit_cmd)
        
        # Keep script running and monitor both processes
        while True:
            time.sleep(1)
            
            # Check if FastAPI crashed
            if fastapi_process.poll() is not None:
                print("\n❌ FastAPI has stopped!")
                cleanup_processes()
                break
            
            # Check if Streamlit crashed
            if streamlit_process.poll() is not None:
                print("\n❌ Streamlit has stopped!")
                cleanup_processes()
                break
                
    except KeyboardInterrupt:
        cleanup_processes()

if __name__ == "__main__":
    main()