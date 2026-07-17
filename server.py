import http.server
import socketserver
import os
import aspose.threed as a3d

PORT = 8000

class ARRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            try:
                # Receive GLB file
                content_length = int(self.headers['Content-Length'])
                glb_data = self.rfile.read(content_length)
                
                # Save GLB
                glb_path = os.path.join("assets", "norscope-experience.glb")
                usdz_path = os.path.join("assets", "norscope-experience.usdz")
                
                # Ensure assets folder exists
                os.makedirs("assets", exist_ok=True)
                
                with open(glb_path, "wb") as f:
                    f.write(glb_data)
                print(f"[Server] Saved {glb_path} ({len(glb_data)} bytes)")
                
                # Convert to USDZ
                a3d.TrialException.set_suppress_trial_exception(True)
                scene = a3d.Scene.from_file(glb_path)
                scene.save(usdz_path)
                print(f"[Server] Successfully converted to {usdz_path}")
                
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"success"}')
            except Exception as e:
                print(f"[Server] Error during upload/conversion: {e}")
                self.send_response(500)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(f'{{"error":"{str(e)}"}}'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def end_headers(self):
        # Add CORS headers to all responses
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

# Run the server
Handler = ARRequestHandler
# Enable reusing address to prevent "address already in use" errors during quick restarts
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"[Server] Running at http://localhost:{PORT}")
    httpd.serve_forever()
