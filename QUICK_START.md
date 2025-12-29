# QuSim Quick Start Guide

## One-Command Launch

Simply run one of these commands in your terminal:

### Windows:
```bash
python launch.py
```

Or double-click:
```
launch.bat
```

### Linux/Mac:
```bash
python3 launch.py
```

Or:
```bash
bash launch.sh
```

## What It Does

The launcher script will:
1. ✅ Start the FastAPI backend server (port 8000)
2. ✅ Start the React frontend (port 3000)
3. ✅ Wait for both servers to be ready
4. ✅ Automatically open your browser to http://localhost:3000
5. ✅ Keep running until you press Ctrl+C

## Access Points

Once launched, you can access:
- **Frontend (Visual Editor)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Stopping the Servers

Press `Ctrl+C` in the terminal where you ran the launcher to stop both servers.

## Troubleshooting

### Port Already in Use
If you see a message that a port is already in use:
- Port 8000: Backend API - kill the process using port 8000
- Port 3000: Frontend - kill the process using port 3000

### Frontend Dependencies Not Installed
The launcher will automatically install dependencies if needed. This may take a minute the first time.

### Browser Doesn't Open
If the browser doesn't open automatically, manually navigate to:
- http://localhost:3000

## Manual Launch (Alternative)

If you prefer to launch manually:

**Terminal 1 (Backend):**
```bash
python run_api.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

Then open http://localhost:3000 in your browser.


