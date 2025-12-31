#!/usr/bin/env python3
"""Wait for frontend to be ready and open browser."""

import socket
import time
import webbrowser

def check_port(port):
    """Check if port is listening."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

print("Waiting for frontend to be ready...")
print("(This can take 30-90 seconds on first run)")

for i in range(120):  # Wait up to 2 minutes
    if check_port(3000):
        print("\nFrontend is ready! Opening browser...")
        webbrowser.open("http://localhost:3000")
        break
    print('.', end='', flush=True)
    time.sleep(1)
else:
    print("\nTimeout waiting for frontend. Please check the frontend window for errors.")

