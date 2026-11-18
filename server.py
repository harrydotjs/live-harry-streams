import os
import re
import sys
import http.server
import socketserver
import socket

PORT = 8080
DIRECTORY = os.getcwd()

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        super().server_bind()
        # Enable TCP_NODELAY to prevent buffering latency
        try:
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception:
            pass

class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    """High-performance multi-threaded HTTP server with full HTTP 206 Partial Content (Byte-Range) streaming."""
    
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS and caching headers for high-throughput video streaming
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Range, Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = self.translate_path(self.path)
        
        # Missing file or directory falls back to standard handler
        if os.path.isdir(path) or not os.path.exists(path):
            return super().do_GET()

        file_size = os.path.getsize(path)
        range_header = self.headers.get('Range')

        # If no Range requested, serve full file
        if not range_header:
            return super().do_GET()

        # Parse Range: bytes=START-END
        m = re.match(r"^bytes=(\d+)-(\d*)", range_header.strip())
        if not m:
            self.send_error(416, "Requested Range Not Satisfiable")
            return

        start = int(m.group(1))
        if m.group(2):
            end = int(m.group(2))
        else:
            # Let the browser buffer smoothly without artificially truncating chunks
            end = file_size - 1

        if start >= file_size or end >= file_size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        total_bytes = (end - start) + 1

        try:
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(path) or "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(total_bytes))
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            # Stream in 128KB chunks: constant tiny RAM footprint (<1MB) with maximum throughput
            with open(path, 'rb', buffering=1024*1024) as f:
                f.seek(start)
                bytes_left = total_bytes
                buf_size = 128 * 1024
                while bytes_left > 0:
                    read_size = min(buf_size, bytes_left)
                    chunk = f.read(read_size)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    bytes_left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # Normal browser behavior when seeking or closing video segments
            pass
        except Exception:
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

    def log_message(self, format, *args):
        # Silence verbose request logging to save CPU cycles
        pass

if __name__ == "__main__":
    with ThreadingTCPServer(("", PORT), RangeRequestHandler) as httpd:
        print(f"[Streaming Server] Multi-threaded HTTP 206 streaming server running on port {PORT}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

