# # launcher.py
# # This script launches two independent services (FastAPI and Streamlit)
# # and monitors them, ensuring a clean shutdown if either fails.

# import subprocess
# import time
# import sys
# import requests
# import os
# import signal
# import threading

# from dotenv import load_dotenv
# load_dotenv()

# # ============================================================================
# # CONFIGURATION
# # ============================================================================

# # Check if the PORT env variable exists (standard for deployment platforms)
# IS_PRODUCTION = bool(os.environ.get('PORT'))

# # Streamlit MUST use the public PORT for the platform to detect the service
# STREAMLIT_PORT = os.environ.get('PORT', '8501')

# # FastAPI runs on a fixed internal port (private to the container)
# FASTAPI_PORT = '8000'

# # Listen on all interfaces (0.0.0.0) in production for external access
# HOST = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'

# # Set the FastAPI URL that Streamlit will use to connect
# FASTAPI_URL = f"http://127.0.0.1:{FASTAPI_PORT}"

# # Global process references
# fastapi_process = None
# streamlit_process = None

# # ============================================================================
# # HELPER FUNCTIONS
# # ============================================================================

# def print_process_output(process, prefix):
#     """Print process output in real-time with a prefix."""
#     try:
#         for line in iter(process.stdout.readline, ''):
#             if line:
#                 print(f"[{prefix}] {line.strip()}", flush=True)
#     except Exception as e:
#         print(f"[{prefix}] Error reading output: {e}", flush=True)

# def check_fastapi_ready(max_attempts=50, delay=2):
#     """
#     Wait for FastAPI to be ready using an internal health check.
    
#     Args:
#         max_attempts: Number of health check attempts (default: 50)
#         delay: Seconds between attempts (default: 2)
#         Total wait time: max_attempts * delay = 100 seconds
#     """
#     print("[WAIT] Waiting for FastAPI to start...", flush=True)
#     health_url = f"{FASTAPI_URL}/health"
    
#     for i in range(max_attempts):
#         # 1. Check if the process died before being ready
#         if fastapi_process and fastapi_process.poll() is not None:
#             exit_code = fastapi_process.poll()
#             print(f"[ERROR] FastAPI process died with exit code: {exit_code}", flush=True)
#             print("[STOP] Common issues:", flush=True)
#             print("   - Missing dependencies (pip install -r requirements.txt)", flush=True)
#             print("   - MongoDB connection failure (check MONGO_URI)", flush=True)
#             print("   - Missing environment variables (GOOGLE_API_KEY)", flush=True)
#             print("   - Syntax errors in main.py", flush=True)
#             return False
            
#         # 2. Try to connect to the health endpoint
#         try:
#             response = requests.get(health_url, timeout=3)
#             if response.status_code == 200:
#                 elapsed_time = (i + 1) * delay
#                 print(f"[OK] FastAPI is ready! (took {elapsed_time} seconds)", flush=True)
#                 return True
#         except requests.exceptions.RequestException as e:
#             # Connection refused or timeout - FastAPI not ready yet
#             pass
        
#         time.sleep(delay)
        
#         # Print progress every 10 attempts (20 seconds)
#         if (i + 1) % 10 == 0:
#             elapsed = (i + 1) * delay
#             total = max_attempts * delay
#             print(f"   Still waiting... ({elapsed}/{total} seconds)", flush=True)
    
#     total_wait = max_attempts * delay
#     print(f"[ERROR] FastAPI failed to respond after {total_wait} seconds", flush=True)
#     print("[TIP] Try increasing the timeout or check FastAPI logs above", flush=True)
#     return False

# def cleanup_processes(signum=None, frame=None):
#     """Clean shutdown of all processes upon termination signals."""
#     global fastapi_process, streamlit_process
    
#     print("\n\n[STOP] Shutting down services...", flush=True)
    
#     # 1. Terminate Streamlit first (frontend should stop before backend)
#     if streamlit_process:
#         print("[WAIT] Stopping Streamlit...", flush=True)
#         streamlit_process.terminate()
#         try:
#             streamlit_process.wait(timeout=5)
#             print("[OK] Streamlit stopped", flush=True)
#         except subprocess.TimeoutExpired:
#             print("[WARN] Force killing Streamlit...", flush=True)
#             streamlit_process.kill()
#             streamlit_process.wait()
    
#     # 2. Terminate FastAPI
#     if fastapi_process:
#         print("[WAIT] Stopping FastAPI...", flush=True)
#         fastapi_process.terminate()
#         try:
#             fastapi_process.wait(timeout=5)
#             print("[OK] FastAPI stopped", flush=True)
#         except subprocess.TimeoutExpired:
#             print("[WARN] Force killing FastAPI...", flush=True)
#             fastapi_process.kill()
#             fastapi_process.wait()
    
#     print("[OK] All services stopped cleanly", flush=True)
#     if signum is not None:
#         sys.exit(0)

# # ============================================================================
# # MAIN LAUNCHER
# # ============================================================================

# def main():
#     global fastapi_process, streamlit_process
    
#     env_name = "PRODUCTION" if IS_PRODUCTION else "DEVELOPMENT"
#     print("="*70, flush=True)
#     print(f">> Project Management Intelligent System - {env_name} Mode", flush=True)
#     print("="*70, flush=True)
    
#     # Display configuration
#     print(f"\nConfiguration:", flush=True)
#     print(f"   Mode: {env_name}", flush=True)
#     print(f"   Host: {HOST}", flush=True)
#     print(f"   Streamlit Port: {STREAMLIT_PORT}", flush=True)
#     print(f"   FastAPI Port: {FASTAPI_PORT}", flush=True)
#     print(f"   FastAPI URL: {FASTAPI_URL}", flush=True)
#     print(f"   MongoDB URI: {'Set [OK]' if os.getenv('MONGO_URI') else 'Missing [X]'}", flush=True)
#     print(f"   Google API Key: {'Set [OK]' if os.getenv('GOOGLE_API_KEY') else 'Missing [X]'}", flush=True)
#     print(f"\n{'='*70}\n", flush=True)
    
#     # Verify required environment variables
#     if not os.getenv('MONGO_URI'):
#         print("[ERROR] MONGO_URI environment variable not set!", flush=True)
#         print("   Set it in your .env file or deployment environment", flush=True)
#         sys.exit(1)
    
#     if not os.getenv('GOOGLE_API_KEY'):
#         print("[WARNING] GOOGLE_API_KEY not set. AI features may not work.", flush=True)
    
#     # Set up signal handlers for graceful shutdown
#     signal.signal(signal.SIGINT, cleanup_processes)
#     signal.signal(signal.SIGTERM, cleanup_processes)
    
#     # --- 1. Start FastAPI (Backend) ---
#     print(f">> Starting FastAPI backend on {HOST}:{FASTAPI_PORT}...", flush=True)
    
#     fastapi_cmd = [
#         sys.executable, "-m", "uvicorn", "main:app",
#         "--host", HOST,
#         "--port", FASTAPI_PORT
#     ]
    
#     # Add reload only in development
#     if not IS_PRODUCTION:
#         fastapi_cmd.append("--reload")
#         print("   (Hot reload enabled)", flush=True)
    
#     # Start FastAPI process with output capture
#     try:
#         fastapi_process = subprocess.Popen(
#             fastapi_cmd,
#             env={**os.environ},
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             bufsize=1  # Line buffered
#         )
        
#         # Start a background thread to print FastAPI logs
#         log_thread = threading.Thread(
#             target=print_process_output,
#             args=(fastapi_process, "FastAPI"),
#             daemon=True
#         )
#         log_thread.start()
        
#     except Exception as e:
#         print(f"❌ Failed to start FastAPI: {e}", flush=True)
#         sys.exit(1)
    
#     # Give FastAPI time to initialize (import modules, load dependencies)
#     initial_delay = 15 if IS_PRODUCTION else 5
#     print(f"[WAIT] Giving FastAPI {initial_delay} seconds to initialize...", flush=True)
#     time.sleep(initial_delay)
    
#     # Check if it crashed during initialization
#     if fastapi_process.poll() is not None:
#         print(f"[ERROR] FastAPI crashed during initialization (exit code: {fastapi_process.poll()})", flush=True)
#         print("   Check the FastAPI logs above for errors", flush=True)
#         sys.exit(1)
    
#     # --- 2. Wait for FastAPI to be ready ---
#     # Give it 100 seconds total (50 attempts × 2 seconds)
#     if not check_fastapi_ready(max_attempts=50, delay=2):
#         print("\n[ERROR] FastAPI failed to start. Exiting.", flush=True)
#         cleanup_processes()
#         sys.exit(1)
    
#     # --- 3. Start Streamlit (Frontend) ---
#     print(f"\n>> Starting Streamlit interface on port {STREAMLIT_PORT}...", flush=True)
    
#     streamlit_cmd = [
#         sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
#         "--server.port", STREAMLIT_PORT,
#         "--server.address", HOST,
#     ]
    
#     # Production-specific flags
#     if IS_PRODUCTION:
#         streamlit_cmd.extend([
#             "--server.headless", "true",
#             "--server.enableCORS", "false",
#             "--server.enableXsrfProtection", "false"
#         ])
#         print("   (Production mode: headless, CORS disabled)", flush=True)
    
#     # Create environment with FASTAPI_URL set
#     streamlit_env = os.environ.copy()
#     streamlit_env['FASTAPI_URL'] = FASTAPI_URL
    
#     try:
#         streamlit_process = subprocess.Popen(
#             streamlit_cmd,
#             env=streamlit_env,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             bufsize=1
#         )
        
#         # Start a background thread to print Streamlit logs
#         streamlit_log_thread = threading.Thread(
#             target=print_process_output,
#             args=(streamlit_process, "Streamlit"),
#             daemon=True
#         )
#         streamlit_log_thread.start()
        
#     except Exception as e:
#         print(f"❌ Failed to start Streamlit: {e}", flush=True)
#         cleanup_processes()
#         sys.exit(1)
    
#     # Give Streamlit a moment to start
#     print("[WAIT] Waiting for Streamlit to initialize...", flush=True)
#     time.sleep(5)
    
#     # --- 4. Final Status Check ---
#     if streamlit_process.poll() is not None:
#         print(f"[ERROR] Streamlit failed to start (exit code: {streamlit_process.poll()})", flush=True)
#         cleanup_processes()
#         sys.exit(1)
    
#     # --- 5. Success! ---
#     print("\n" + "="*70, flush=True)
#     print("[OK] All services started successfully!", flush=True)
#     print("="*70, flush=True)
    
#     if IS_PRODUCTION:
#         print(f"\n[INFO] Application available on port: {STREAMLIT_PORT}", flush=True)
#         print(f"[INFO] API running on internal port: {FASTAPI_PORT}", flush=True)
#     else:
#         print(f"\n[INFO] Streamlit UI: http://localhost:{STREAMLIT_PORT}", flush=True)
#         print(f"[INFO] FastAPI docs: http://localhost:{FASTAPI_PORT}/docs", flush=True)
#         print(f"[INFO] Health check: http://localhost:{FASTAPI_PORT}/health", flush=True)
    
#     print(f"\n[TIP] Press Ctrl+C to stop all services", flush=True)
#     print("="*70 + "\n", flush=True)
    
#     # --- 6. Monitor Processes ---
#     print("[INFO] Monitoring processes (logs will appear below)...\n", flush=True)
    
#     try:
#         while True:
#             time.sleep(3)
            
#             # Check FastAPI
#             if fastapi_process.poll() is not None:
#                 exit_code = fastapi_process.poll()
#                 print(f"\n[ERROR] FastAPI terminated unexpectedly (exit code: {exit_code})", flush=True)
#                 print("[STOP] Shutting down all services...", flush=True)
#                 cleanup_processes()
#                 sys.exit(1)
            
#             # Check Streamlit
#             if streamlit_process.poll() is not None:
#                 exit_code = streamlit_process.poll()
#                 print(f"\n[ERROR] Streamlit terminated unexpectedly (exit code: {exit_code})", flush=True)
#                 print("[STOP] Shutting down all services...", flush=True)
#                 cleanup_processes()
#                 sys.exit(1)
            
#     except KeyboardInterrupt:
#         print("\n[INFO] Keyboard interrupt received", flush=True)
#         cleanup_processes()
#         sys.exit(0)

# # ============================================================================
# # ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     main()

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