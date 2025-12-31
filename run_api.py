#!/usr/bin/env python3
"""
Run the QuSim API server.
"""

import uvicorn
from qusim.api.main import app

if __name__ == "__main__":
    uvicorn.run("qusim.api.main:app", host="0.0.0.0", port=8000, reload=True)


