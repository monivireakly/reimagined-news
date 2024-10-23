import subprocess
import os
import sys
import time

def run_backend():
    os.chdir("news-sentiment-backend")
    print("Starting backend on port 8081")
    process = subprocess.Popen(["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081", "--reload"])
    os.chdir("..")
    return process

def run_frontend():
    os.chdir("news-sentiment-frontend")
    print("Starting frontend on port 5051")
    env = os.environ.copy()
    env["NEXT_PUBLIC_API_URL"] = "http://localhost:8081"
    process = subprocess.Popen(["npm", "run", "dev", "--", "--port", "5051"], env=env)
    os.chdir("..")
    return process

if __name__ == "__main__":
    try:
        backend_process = run_backend()
        time.sleep(2)  # Give the backend a moment to start
        frontend_process = run_frontend()

        print("Backend running on http://localhost:8081")
        print("Frontend running on http://localhost:5051")

        # Keep the script running
        backend_process.wait()
        frontend_process.wait()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Shutting down...")
        if 'backend_process' in locals():
            backend_process.terminate()
        if 'frontend_process' in locals():
            frontend_process.terminate()
