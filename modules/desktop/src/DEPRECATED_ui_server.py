import http.server
import socketserver
import os
import sys

PORT = 3000
DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_ui_server():
    if not os.path.exists(DIRECTORY):
        print(f"UI directory not found: {DIRECTORY}")
        sys.exit(1)
        
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"CerynixAI UI Server running at http://localhost:{PORT}")
        print("Serving files from", DIRECTORY)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down UI Server.")
            sys.exit(0)

if __name__ == "__main__":
    start_ui_server()
