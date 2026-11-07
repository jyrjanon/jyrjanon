"""Vercel serverless function: /api/svg?s=hero|wordmark|projects|stats|heatmap
Builds the SVG fresh from live GitHub data on every request (45 s in-memory cache to protect the API rate limit)."""
import os, sys, time, copy
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import generate as g

_cache = {"t": 0, "d": None, "stamp": ""}

def live_data():
    if time.time() - _cache["t"] > 45:
        d = g.fetch_live(copy.deepcopy(g.DATA))
        _cache.update(t=time.time(), d=d, stamp=g.STAMP)
    g.STAMP = _cache["stamp"]
    return _cache["d"]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        sec = parse_qs(urlparse(self.path).query).get("s", ["hero"])[0]
        try:
            body = g.out[sec](live_data()).encode(); code = 200
        except Exception as e:
            body = f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="40"><text x="10" y="25" fill="red">error: {e}</text></svg>'.encode(); code = 500
        self.send_response(code)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Cache-Control", "public, max-age=0, s-maxage=60, stale-while-revalidate=30")
        self.end_headers(); self.wfile.write(body)
