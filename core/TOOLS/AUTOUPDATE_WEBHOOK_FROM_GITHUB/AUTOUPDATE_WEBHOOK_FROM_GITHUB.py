#!/usr/bin/env python3
"""
GitHub Webhook Listener for Auto-Update
Listens for GitHub push events and automatically updates the application
"""
import http.server
import socketserver
import os
import hmac
import hashlib
import subprocess
import threading

PORT = 9000
SECRET = os.environ.get("AUTOUPDATE_WEBHOOK_FROM_GITHUB", "").encode("utf-8")
UpdateLock = threading.Lock()

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/push_and_update_server":
            self.send_error(404, "Not Found")
            return

        # Get headers
        content_length = int(self.headers.get("Content-Length", 0))
        hub_signature = self.headers.get("X-Hub-Signature")

        # Read payload
        payload = self.rfile.read(content_length)

        # Verify signature
        if SECRET:
            if not hub_signature:
                self.send_error(403, "Forbidden: Missing Signature")
                return

            sha_name, signature = hub_signature.split('=')
            if sha_name != 'sha1':
                self.send_error(501, "Not Implemented: Only SHA1 supported")
                return

            mac = hmac.new(SECRET, msg=payload, digestmod=hashlib.sha1)
            if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
                self.send_error(403, "Forbidden: Invalid Signature")
                return

        # Respond immediately to avoid GitHub timeout
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Update triggered successfully")

        # Run update in a separate thread
        if not UpdateLock.locked():
            threading.Thread(target=self.run_update).start()
        else:
            print("Update already in progress. Skipping.", flush=True)

    def run_update(self):
        if not UpdateLock.acquire(blocking=False):
            return

        try:
            print("=" * 80, flush=True)
            print("Received valid webhook. Starting update process...", flush=True)
            print("=" * 80, flush=True)

            # Execute git pull
            print("Step 1: Running git pull...", flush=True)
            subprocess.check_call(["git", "pull"], cwd="/app", stderr=subprocess.STDOUT)

            # Execute docker compose down and up
            print("Step 2: Stopping old containers...", flush=True)
            subprocess.check_call(
                ["docker-compose", "-p", "flask-cards", "down"],
                cwd="/app",
                stderr=subprocess.STDOUT
            )

            print("Step 3: Building and starting new containers...", flush=True)
            subprocess.check_call(
                ["docker-compose", "-p", "flask-cards", "up", "-d", "--build", "flask_app"],
                cwd="/app",
                stderr=subprocess.STDOUT
            )

            print("=" * 80, flush=True)
            print("Update completed successfully!", flush=True)
            print("=" * 80, flush=True)

        except subprocess.CalledProcessError as e:
            print(f"ERROR during update: {e}", flush=True)
        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}", flush=True)
        finally:
            UpdateLock.release()

    def do_GET(self):
        """Health check endpoint"""
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Webhook listener is running")
        else:
            self.send_error(404, "Not Found")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
        print(f"=" * 80, flush=True)
        print(f"GitHub Webhook Listener started on port {PORT}", flush=True)
        print(f"Webhook URL: http://your-server:9000/push_and_update_server", flush=True)
        print(f"Health check: http://your-server:9000/health", flush=True)
        print(f"Secret configured: {'Yes' if SECRET else 'No (WARNING: No security!)'}", flush=True)
        print(f"=" * 80, flush=True)
        httpd.serve_forever()
