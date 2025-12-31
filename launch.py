#!/usr/bin/env python3
"""
QuSim Launcher - Kills existing instances and starts fresh servers.
Automatically opens browser when ready.
"""

import subprocess
import sys
import time
import webbrowser
import socket
import os
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def kill_port(port):
    """Kill any process using the specified port."""
    if sys.platform == 'win32':
        try:
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        try:
                            subprocess.run(
                                ['taskkill', '/F', '/PID', pid], 
                                capture_output=True, 
                                check=False
                            )
                            print(f"   Killed process on port {port} (PID: {pid})")
                        except:
                            pass
        except:
            pass
    else:
        try:
            subprocess.run(
                ['lsof', '-ti', f':{port}', '|', 'xargs', 'kill', '-9'],
                shell=True, 
                capture_output=True
            )
        except:
            pass

def check_port(port, timeout=2):
    """Check if a port is listening."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def wait_for_port(port, name, max_wait=60):
    """Wait for a port to become available."""
    print(f"   Waiting for {name}...", end='', flush=True)
    for i in range(max_wait):
        if check_port(port):
            print(f" Ready!")
            return True
        if i % 5 == 0 and i > 0:
            print(f" ({i}s)", end='', flush=True)
        else:
            print('.', end='', flush=True)
        time.sleep(1)
    print(f" Timeout after {max_wait}s!")
    return False

def get_python_exe():
    """Get the Python executable from venv if it exists, otherwise use system Python."""
    project_dir = Path(__file__).parent
    if sys.platform == 'win32':
        venv_python = project_dir / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_dir / "venv" / "bin" / "python"
    
    if venv_python.exists():
        return str(venv_python)
    return sys.executable

def find_npm():
    """Find npm executable on the system."""
    if sys.platform == 'win32':
        # Try common locations
        common_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            r"C:\Program Files\nodejs\npm.ps1",
            r"C:\Program Files (x86)\nodejs\npm.ps1",
        ]
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(
                ['where.exe', 'npm'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                npm_path = result.stdout.strip().split('\n')[0]
                if Path(npm_path).exists():
                    return npm_path
        except:
            pass
    
    # Default: just use 'npm' and hope it's in PATH
    return 'npm'

def check_npm():
    """Check if npm is installed and accessible."""
    npm_exe = find_npm()
    
    try:
        # Try to run npm --version
        if sys.platform == 'win32' and npm_exe.endswith('.cmd'):
            result = subprocess.run(
                ['cmd', '/c', npm_exe, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            result = subprocess.run(
                [npm_exe, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   Found npm version: {version}")
            return True, npm_exe
    except:
        pass
    
    return False, None

def start_backend():
    """Start the backend server."""
    print("\n[BACKEND] Starting Backend API (port 8000)...")
    kill_port(8000)
    time.sleep(1)
    
    project_dir = Path(__file__).parent
    python_exe = get_python_exe()
    
    if sys.platform == 'win32':
        # Quote the Python path for Windows
        cmd_str = f'"{python_exe}" run_api.py'
        subprocess.Popen(
            ['start', 'cmd', '/k', cmd_str],
            cwd=project_dir,
            shell=True
        )
    else:
        subprocess.Popen(
            [python_exe, 'run_api.py'],
            cwd=project_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    return wait_for_port(8000, "Backend", max_wait=30)

def start_frontend():
    """Start the frontend server."""
    print("\n[FRONTEND] Starting Frontend (port 3000)...")
    kill_port(3000)
    time.sleep(1)
    
    # Check for npm
    npm_available, npm_exe = check_npm()
    if not npm_available:
        print("\n[ERROR] npm is not found!")
        print("Please install Node.js from https://nodejs.org/")
        print("After installing, restart your terminal and try again.")
        return False
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if node_modules exists and if ajv is properly installed
    needs_install = False
    if not (frontend_dir / "node_modules").exists():
        needs_install = True
    else:
        # Check if ajv is installed correctly
        ajv_path = frontend_dir / "node_modules" / "ajv" / "dist" / "compile" / "codegen.js"
        if not ajv_path.exists():
            print("   Detected dependency issues, reinstalling...")
            needs_install = True
    
    if needs_install:
        print("   Installing/Reinstalling dependencies...")
        # Clean install
        if (frontend_dir / "node_modules").exists():
            import shutil
            try:
                shutil.rmtree(frontend_dir / "node_modules")
            except:
                pass
        
        # Use the found npm executable
        if sys.platform == 'win32' and npm_exe.endswith('.cmd'):
            subprocess.run(
                ['cmd', '/c', npm_exe, 'install', '--legacy-peer-deps'],
                cwd=frontend_dir,
                check=True
            )
        else:
            subprocess.run(
                [npm_exe, 'install', '--legacy-peer-deps'],
                cwd=frontend_dir,
                check=True
            )
    
    if sys.platform == 'win32':
        # Start in new window - use the found npm executable
        if npm_exe.endswith('.cmd'):
            cmd_str = f'cmd /c "{npm_exe}" start'
        else:
            cmd_str = f'"{npm_exe}" start'
        subprocess.Popen(
            ['start', 'cmd', '/k', cmd_str],
            cwd=frontend_dir,
            shell=True
        )
    else:
        subprocess.Popen(
            [npm_exe, 'start'],
            cwd=frontend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    return wait_for_port(3000, "Frontend", max_wait=120)

def open_browser(url="http://localhost:3000", max_attempts=3):
    """Open browser with retry logic."""
    for attempt in range(max_attempts):
        try:
            webbrowser.open(url)
            print(f"   Browser opened! ({url})")
            return True
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"   Attempt {attempt + 1} failed, retrying...")
                time.sleep(1)
            else:
                print(f"   Failed to open browser: {e}")
                print(f"   Please manually open: {url}")
                return False
    return False

def wait_and_open_browser():
    """Wait for frontend to be ready and open browser."""
    print("\n[BROWSER] Waiting for frontend to be ready...")
    max_wait = 150  # 2.5 minutes
    check_interval = 2  # Check every 2 seconds
    
    for i in range(0, max_wait, check_interval):
        if check_port(3000):
            print("   Frontend is ready!")
            time.sleep(3)  # Give it a moment to fully initialize
            return open_browser()
        
        if i > 0 and i % 20 == 0:
            print(f"   Still waiting... ({i}/{max_wait}s)")
        time.sleep(check_interval)
    
    print(f"   Timeout after {max_wait}s waiting for frontend.")
    print("   You can manually open: http://localhost:3000")
    return False

def main():
    """Main launcher."""
    print("=" * 70)
    print("  QuSim Quantum Circuit Simulator - Launcher")
    print("=" * 70)
    
    # Check npm early
    print("\n[CHECK] Verifying prerequisites...")
    npm_available, _ = check_npm()
    if not npm_available:
        print("\n[ERROR] npm is not found!")
        print("Please install Node.js from https://nodejs.org/")
        print("After installing, restart your terminal and try again.")
        sys.exit(1)
    
    print("\n[INIT] Stopping any existing instances...")
    kill_port(8000)
    kill_port(3000)
    time.sleep(2)
    
    try:
        # Start backend
        if not start_backend():
            print("\n[ERROR] Failed to start backend. Check for errors above.")
            return
        
        # Start frontend
        if not start_frontend():
            print("\n[ERROR] Failed to start frontend. Check for errors above.")
            return
        
        # Success!
        print("\n" + "=" * 70)
        print("  [SUCCESS] QuSim is ready!")
        print("=" * 70)
        print("\nAccess points:")
        print("   - Frontend: http://localhost:3000")
        print("   - Backend API: http://localhost:8000")
        print("   - API Docs: http://localhost:8000/docs")
        print("\nNote: Servers are running in separate windows.")
        print("      Close those windows to stop the servers.")
        print("=" * 70)
        
        # Wait for frontend and open browser
        wait_and_open_browser()
        
        # Keep script alive
        print("\n[INFO] Launcher will stay active. Press Ctrl+C to exit.")
        print("       (Servers will continue running in their own windows)")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n\n[EXIT] Launcher stopped. Servers are still running.")
            print("       Close the server windows to stop them.")
    
    except KeyboardInterrupt:
        print("\n\n[EXIT] Interrupted. Exiting...")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
