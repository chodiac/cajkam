"""Local preview: python tools/serve.py [port]  (default 5186)."""
import http.server
import socketserver
import sys
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5186


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml'}

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        if code == 404 and (ROOT / '404.html').exists():
            body = (ROOT / '404.html').read_bytes()
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)

    def do_POST(self):
        """Dev-only: POST /__save?media/<name>.jpg stores a rendered still
        (used once to export the hero poster from the canvas film)."""
        target = self.path.split('?', 1)[-1]
        if not self.path.startswith('/__save?') or not target.startswith('media/') or '..' in target:
            self.send_error(403)
            return
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        (ROOT / target).write_bytes(body)
        self.send_response(204)
        self.end_headers()

    def log_message(self, *a):
        pass


socketserver.ThreadingTCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), partial(Handler, directory=str(ROOT))) as s:
    print(f'Cajka M preview on http://localhost:{PORT}', flush=True)
    s.serve_forever()
