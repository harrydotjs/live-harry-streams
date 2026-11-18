import os
import re
import sys
import http.server
import socketserver

PORT = 8080
DIRECTORY = os.getcwd()

class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with full HTTP 206 Partial Content (Byte-Range) support for video seeking."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        path = self.translate_path(self.path)
        
        # Non-file or missing file falls back to standard handler
        if os.path.isdir(path) or not os.path.exists(path):
            return super().do_GET()

        file_size = os.path.getsize(path)
        range_header = self.headers.get('Range')

        # If no Range requested, serve file normally (200 OK)
        if not range_header:
            return super().do_GET()

        # Parse Range: bytes=START-END
        m = re.match(r"^bytes=(\d+)-(\d*)", range_header)
        if not m:
            self.send_error(416, "Requested Range Not Satisfiable")
            return

        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else file_size - 1

        if start >= file_size or end >= file_size or start > end:
            self.send_error(416, "Requested Range Not Satisfiable")
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.end_headers()
            return

        chunk_size = (end - start) + 1

        try:
            with open(path, 'rb') as f:
                f.seek(start)
                data = f.read(chunk_size)

            # Send HTTP 206 Partial Content (enables instant video seeking in Chrome/Firefox/Safari)
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(path) or "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            # Client disconnected or seek aborted
            pass

    def do_HEAD(self):
        path = self.translate_path(self.path)
        if os.path.isfile(path):
            file_size = os.path.getsize(path)
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(path) or "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()
        else:
            super().do_HEAD()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RangeRequestHandler) as httpd:
        print(f"[Streaming Server] Serving on port {PORT} with full HTTP 206 Range seeking support...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
