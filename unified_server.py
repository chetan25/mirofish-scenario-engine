#!/usr/bin/env python3
"""
Unified HTTP Server - Serves frontend AND proxies API requests to backend
Allows single Cloudflare tunnel to serve both frontend (port 3000) and backend (proxied via /api)
"""

import http.server
import socketserver
import json
from pathlib import Path
import urllib.request
import urllib.error

class UnifiedHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve static files
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            # Serve from current directory
            self.directory = '/root/side-hustle-simulator'
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/') or self.path == '/simulate':
            self.proxy_to_backend()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def proxy_to_backend(self):
        """Proxy /api/* requests to http://localhost:5001/*"""
        # Remove /api prefix and forward to backend
        backend_path = self.path.replace('/api', '')
        backend_url = f'http://localhost:5001{backend_path}'
        
        print(f"[PROXY] {self.command} {self.path} -> {backend_url}")
        
        try:
            # Read request body if POST
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length else None
            
            # Create backend request
            req = urllib.request.Request(
                backend_url,
                data=body,
                method=self.command,
                headers={
                    'Content-Type': self.headers.get('Content-Type', 'application/json'),
                }
            )
            
            # Make request to backend
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read()
                
                # Send response back
                self.send_response(response.status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', len(response_data))
                self.end_headers()
                self.wfile.write(response_data)
                
                print(f"[PROXY] ✓ {response.status}")
        
        except urllib.error.HTTPError as e:
            error_data = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(error_data))
            self.end_headers()
            self.wfile.write(error_data)
            print(f"[PROXY] ✗ {e.code}")
        
        except Exception as e:
            error_msg = json.dumps({'error': str(e)}).encode()
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(error_msg))
            self.end_headers()
            self.wfile.write(error_msg)
            print(f"[PROXY] ✗ Error: {e}")

if __name__ == '__main__':
    PORT = 3000
    Handler = UnifiedHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"""
╔════════════════════════════════════════╗
║   Side Hustle Simulator - Unified      ║
║   Frontend + API Proxy Server          ║
╚════════════════════════════════════════╝

🌐 Frontend:    http://localhost:3000
🔗 API Proxy:   http://localhost:3000/api/* → localhost:5001/*
📡 Backend:     http://localhost:5001

✅ Running on port {PORT}
Press Ctrl+C to stop
""")
        httpd.serve_forever()
