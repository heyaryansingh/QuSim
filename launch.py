#!/usr/bin/env python3
"""
Launch script for QuSim - starts backend and frontend, opens browser.
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_port(port):
    """Check if a port is already in use."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting QuSim Backend API...")
    if sys.platform == 'win32':
        # On Windows, use start to open in new window
        backend_process = subprocess.Popen(
            ["start", "cmd", "/k", f"{sys.executable} run_api.py"],
            cwd=Path(__file__).parent,
            shell=True
        )
    else:
        backend_process = subprocess.Popen(
            [sys.executable, "run_api.py"],
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    return backend_process

def start_frontend():
    """Start the React frontend development server."""
    print("🎨 Starting QuSim Frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies (this may take a minute)...")
        subprocess.run(
            ["npm", "install", "--legacy-peer-deps"],
            cwd=frontend_dir,
            check=True
        )
    
    if sys.platform == 'win32':
        # On Windows, use start to open in new window
        frontend_process = subprocess.Popen(
            ["start", "cmd", "/k", "npm start"],
            cwd=frontend_dir,
            shell=True
        )
    else:
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    return frontend_process

def wait_for_server(port, name, timeout=60):
    """Wait for a server to be ready on the given port."""
    import socket
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port(port):
            print(f"✅ {name} is ready on port {port}")
            return True
        time.sleep(1)
    return False

def main():
    """Main launcher function."""
    print("=" * 60)
    print("  QuSim Quantum Circuit Simulator - Launcher")
    print("=" * 60)
    print()
    
    # Check if ports are already in use
    if check_port(8000):
        print("⚠️  Port 8000 is already in use. Backend may already be running.")
    if check_port(3000):
        print("⚠️  Port 3000 is already in use. Frontend may already be running.")
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(2)  # Give backend a moment to start
        
        # Start frontend
        frontend_process = start_frontend()
        time.sleep(3)  # Give frontend a moment to start
        
        # Wait for servers to be ready
        print("\n⏳ Waiting for servers to start...")
        backend_ready = wait_for_server(8000, "Backend API", timeout=30)
        frontend_ready = wait_for_server(3000, "Frontend", timeout=60)
        
        if backend_ready and frontend_ready:
            print("\n" + "=" * 60)
            print("  ✅ QuSim is ready!")
            print("=" * 60)
            print("\n📍 Access the application:")
            print("   Frontend: http://localhost:3000")
            print("   Backend API: http://localhost:8000")
            print("   API Docs: http://localhost:8000/docs")
            print("\n💡 Press Ctrl+C to stop all servers")
            print("=" * 60)
            
            # Open browser after a short delay
            time.sleep(2)
            print("\n🌐 Opening browser...")
            webbrowser.open("http://localhost:3000")
            
            # Keep script running
            try:
                print("\n💡 Servers are running in separate windows.")
                print("   Close those windows or press Ctrl+C here to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down servers...")
                try:
                    if sys.platform == 'win32':
                        # On Windows, try to kill processes by port
                        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq *run_api*"], 
                                     capture_output=True)
                        subprocess.run(["taskkill", "/F", "/IM", "node.exe"], capture_output=True)
                    else:
                        backend_process.terminate()
                        frontend_process.terminate()
                except:
                    pass
                print("✅ Servers stopped. Goodbye!")
        else:
            print("\n❌ Failed to start servers. Please check the error messages above.")
            try:
                if sys.platform != 'win32':
                    backend_process.terminate()
                    frontend_process.terminate()
            except:
                pass
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        try:
            if sys.platform != 'win32':
                if 'backend_process' in locals():
                    backend_process.terminate()
                if 'frontend_process' in locals():
                    frontend_process.terminate()
        except:
            pass
        print("✅ Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        try:
            if sys.platform != 'win32':
                if 'backend_process' in locals():
                    backend_process.terminate()
                if 'frontend_process' in locals():
                    frontend_process.terminate()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
