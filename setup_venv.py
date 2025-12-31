#!/usr/bin/env python3
"""
Setup virtual environment for QuSim.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and handle errors."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Warning: {result.stderr}", file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}", file=sys.stderr)
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        raise

def main():
    """Main setup function."""
    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv"
    
    print("=" * 70)
    print("  QuSim - Virtual Environment Setup")
    print("=" * 70)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9 or higher is required!")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    print(f"Project directory: {project_dir}")
    
    # Create virtual environment
    if venv_dir.exists():
        print("\n[INFO] Virtual environment already exists.")
        response = input("Recreate? (y/N): ").strip().lower()
        if response == 'y':
            import shutil
            print("Removing existing virtual environment...")
            shutil.rmtree(venv_dir)
        else:
            print("Using existing virtual environment.")
    
    if not venv_dir.exists():
        print("\n[1/4] Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", str(venv_dir)])
    
    # Determine activation script path
    if sys.platform == 'win32':
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    print(f"\n[2/4] Upgrading pip...")
    # Use python -m pip instead of pip.exe directly (fixes Windows issue)
    result = run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=False)
    if result.returncode != 0:
        print("   Note: Pip upgrade had issues, but continuing (pip is already installed)...")
    
    print(f"\n[3/4] Installing project dependencies...")
    run_command([str(pip_exe), "install", "-e", "."])
    
    print(f"\n[4/4] Verifying installation...")
    result = run_command([str(python_exe), "-c", "import qusim; print('QuSim installed successfully!')"], check=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("  [SUCCESS] Virtual environment setup complete!")
        print("=" * 70)
        print("\nTo activate the virtual environment:")
        if sys.platform == 'win32':
            print(f"  {venv_dir}\\Scripts\\activate")
        else:
            print(f"  source {venv_dir}/bin/activate")
        print("\nOr use the launcher: python launch.py")
    else:
        print("\n[ERROR] Installation verification failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

