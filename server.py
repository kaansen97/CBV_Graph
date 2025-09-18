#!/usr/bin/env python3
"""
Simple HTTP server for the CBV Graph keyword visualization system.
This server properly serves JSON files and static HTML content to avoid CORS issues.
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve files with proper CORS headers and content types."""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def guess_type(self, path):
        """Override to ensure proper JSON content type."""
        import mimetypes
        
        if path.endswith('.json'):
            return 'application/json'
        elif path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.css'):
            return 'text/css'
        
        mimetype, encoding = mimetypes.guess_type(path)
        return mimetype or 'application/octet-stream'
    
    def do_GET(self):
        """Handle GET requests with custom logic."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.path = '/index.html'
        
        super().do_GET()
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging."""
        print(f"[{self.address_string()}] {format % args}")

def start_server(port=8000):
    """Start the HTTP server on the specified port."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    required_files = ['index.html', 'graph.html', 'cbv_data.json']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("⚠️  Warning: Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nMake sure to run 'parse_thesaurus.py' first to generate the JSON files.")
        print("Continuing anyway...")
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 CBV Graph Server Starting...")
            print(f"📁 Serving files from: {os.getcwd()}")
            print(f"📊 Access the keyword explorer: http://localhost:{port}")
            print("\n💡 Available endpoints:")
            print(f"   • Main interface: http://localhost:{port}")
            print("\n⌨️  Press Ctrl+C to stop the server")
            print("-" * 60)
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48: 
            print(f"❌ Error: Port {port} is already in use.")
            print(f"💡 Try a different port: python server.py {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            if not (1024 <= port <= 65535):
                print("❌ Port must be between 1024 and 65535")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid port number. Using default port 8000.")
            port = 8000
    
    start_server(port)