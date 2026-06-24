#!/usr/bin/env python3
"""
HTTP Proxy Server - Forwards API requests to MiroFish backend
Allows Cloudflare tunnel to access localhost:5001
"""

import http.server
import socketserver
from urllib.parse import urlparse
import requests
import json

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/') or self.path == '/simulate':
            self.proxy_request()
        else:
            super().do_POST()
    
    def proxy_request(self):
        # Route API calls to backend
        backend_url = f'http://localhost:5001{self.path}'
        
        try:
            # Get request body if POST
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length else None
            
            # Make request to backend
            response = requests.request(
                method=self.command,
                url=backend_url,
                headers={k: v for k, v in self.headers.items() if k.lower() not in ['host', 'content-length']},
                data=body,
                timeout=30
            )
            
            # Send response back
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    PORT = 3000
    Handler = ProxyHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Proxy server running on port {PORT}")
        print(f"   Frontend: http://localhost:{PORT}")
        print(f"   API Proxy: http://localhost:{PORT}/api/* → http://localhost:5001/*")
        print(f"   Direct: http://localhost:5001 (backend)")
        httpd.serve_forever()
