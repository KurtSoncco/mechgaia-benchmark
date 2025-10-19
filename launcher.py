#!/usr/bin/env python3
"""
AgentBeats Launcher Service

This service acts as a launcher for the MechGAIA green agent on the AgentBeats platform.
It provides a simple HTTP interface that forwards requests to the main agent service.
"""

import os
import json
import time
import signal
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from typing import Dict, Any
import urllib.request
import urllib.error


class LauncherHandler(BaseHTTPRequestHandler):
    """HTTP handler for the launcher service."""
    
    def __init__(self, *args, **kwargs):
        self.agent_url = os.environ.get('AGENT_URL', 'http://localhost:8080')
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            if self.path == '/health':
                self._handle_health()
            elif self.path == '/info':
                self._handle_info()
            elif self.path == '/launch':
                self._handle_launch()
            else:
                self._handle_not_found()
        except Exception as e:
            self._handle_error(f"Handler error: {e}")
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            if self.path == '/launch':
                self._handle_launch_post()
            else:
                self._handle_not_found()
        except Exception as e:
            self._handle_error(f"POST handler error: {e}")
    
    def _handle_health(self):
        """Handle health check requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Check if agent service is available
        agent_healthy = self._check_agent_health()
        
        response = {
            "status": "healthy" if agent_healthy else "degraded",
            "service": "launcher",
            "agent_available": agent_healthy,
            "agent_url": self.agent_url,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_info(self):
        """Handle info requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        info = {
            "service": "launcher",
            "version": "0.1.0",
            "description": "AgentBeats launcher service for MechGAIA green agent",
            "agent_url": self.agent_url,
            "endpoints": {
                "health": "/health",
                "info": "/info",
                "launch": "/launch"
            }
        }
        
        self.wfile.write(json.dumps(info, indent=2).encode())
    
    def _handle_launch(self):
        """Handle launch requests (GET)."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "MechGAIA Green Agent Launcher",
            "status": "ready",
            "agent_url": self.agent_url,
            "instructions": "Send POST request to /launch with agent state"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def _handle_launch_post(self):
        """Handle launch requests (POST)."""
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    state = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    self._handle_error("Invalid JSON in request body")
                    return
            else:
                state = {}
            
            # Forward to agent service
            result = self._forward_to_agent(state)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self._handle_error(f"Launch error: {e}")
    
    def _handle_not_found(self):
        """Handle 404 errors."""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "error": "Not Found",
            "message": f"Endpoint {self.path} not found",
            "available_endpoints": ["/health", "/info", "/launch"]
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_error(self, error_message):
        """Handle errors."""
        try:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "error": "Internal Server Error",
                "message": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
        except:
            pass
    
    def _check_agent_health(self) -> bool:
        """Check if the agent service is healthy."""
        try:
            response = urllib.request.urlopen(f"{self.agent_url}/health", timeout=5)
            return response.status == 200
        except:
            return False
    
    def _forward_to_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Forward request to the agent service."""
        try:
            # Prepare request data
            data = json.dumps(state).encode('utf-8')
            
            # Create request
            req = urllib.request.Request(
                f"{self.agent_url}/evaluate",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Send request
            response = urllib.request.urlopen(req, timeout=30)
            
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
            else:
                return {
                    "error": f"Agent service returned status {response.status}",
                    "status": response.status
                }
                
        except urllib.error.URLError as e:
            return {
                "error": f"Failed to connect to agent service: {e}",
                "agent_url": self.agent_url
            }
        except Exception as e:
            return {
                "error": f"Error forwarding to agent: {e}"
            }
    
    def log_message(self, format, *args):
        """Disable logging."""
        pass


def get_port() -> int:
    """Get the port number from environment variables."""
    try:
        port_str = os.environ.get('LAUNCHER_PORT') or os.environ.get('PORT', '8081')
        if not port_str or not port_str.strip():
            port_str = '8081'
        port_str = port_str.strip()
        port = int(port_str)
        
        if not (1 <= port <= 65535):
            print(f"Warning: Port {port} out of range, using 8081")
            port = 8081
            
        return port
    except (ValueError, TypeError) as e:
        print(f"Warning: Invalid port configuration: {e}, using 8081")
        return 8081


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}, shutting down launcher gracefully...")
    sys.exit(0)


def main():
    """Main entry point for the launcher service."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get configuration
    port = get_port()
    agent_url = os.environ.get('AGENT_URL', 'http://localhost:8080')
    
    print(f"Starting AgentBeats Launcher Service")
    print(f"Port: {port}")
    print(f"Agent URL: {agent_url}")
    
    try:
        # Create and start server
        server = HTTPServer(('0.0.0.0', port), LauncherHandler)
        print(f"Launcher service started on port {port}")
        print(f"Health endpoint: http://0.0.0.0:{port}/health")
        print(f"Info endpoint: http://0.0.0.0:{port}/info")
        print(f"Launch endpoint: http://0.0.0.0:{port}/launch")
        
        server.serve_forever()
        
    except Exception as e:
        print(f"Failed to start launcher service: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Launcher service shutting down")


if __name__ == "__main__":
    main()
