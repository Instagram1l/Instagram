"""أدوات الاستطلاع: نطاقات، DNS، whois، مواقع حية"""
from pathlib import Path

from ..utils import run_local, check_tool


class ReconTools:
    def subdomain_enum(self, domain, deep=False):
        domain = (domain or "").strip()
        if not domain:
            return {"ok": False, "output": "أدخل نطاقًا صالحًا"}
        if not check_tool("subfinder"):
            return {"ok": False, "output": "❌ subfinder غير مثبت — شغّل install_tools.sh"}
        cmd = f"subfinder -d {domain} -silent -all"
        if deep:
            cmd += " -recursive"
        r = run_local(cmd, timeout=1800)
        subs = sorted({
            s.strip() for s in r["output"].splitlines()
            if s.strip() and not s.startswith("[") and " " not in s
        })
        r["subdomains"] = subs
        r["count"] = len(subs)
        if subs:
            r["output"] = f"✅ تم اكتشاف {len(subs)} نطاق فرعي:\n" + "\n".join(subs)
        return r

    def dns_lookup(self, domain):
        domain = (domain or "").strip()
        lines = []
        for rtype in ("A", "AAAA", "MX", "TXT", "NS", "SOA", "CNAME"):
            r = run_local(f"dig +short {domain} {rtype}", timeout=60)
            lines.append(f"[{rtype}] {r['output'] or '—'}")
        r2 = run_local(f"dig @8.8.8.8 {domain} AXFR +time=5 +tries=1", timeout=30)
        if "Transfer failed" not in r2["output"] and r2["output"].strip():
            lines.append(f"[AXFR] ⚠️ Zone Transfer مسموح!\n{r2['output']}")
        else:
            lines.append("[AXFR] مغلق (طبيعي)")
        return {"ok": True, "output": "\n".join(lines)}

    def whois_lookup(self, target):
        target = (target or "").strip()
        if not check_tool("whois"):
            return {"ok": False, "output": "❌ whois غير مثبت"}
        return run_local(f"whois {target}", timeout=120)

    def http_probe(self, targets):
        targets = (targets or "").strip()
        if not targets:
            return {"ok": False, "output": "أدخل نطاقًا أو مسار ملف"}
        if check_tool("httpx"):
            return run_local(
                f"httpx -silent -title -status-code -tech-detect -location -t 50 {targets}",
                timeout=900,
            )
        # بديل يدوي بدون httpx
        import re
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if Path(targets).exists():
            candidates = [l.strip() for l in Path(targets).read_text().splitlines() if l.strip()]
        else:
            candidates = [targets]
        lines = []
        for t in candidates:
            url = t if t.startswith("http") else f"https://{t}"
            try:
                resp = requests.get(url, timeout=10, verify=False, allow_redirects=True)
                m = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.I | re.S)
                title = m.group(1).strip()[:80] if m else ""
                lines.append(f"[{resp.status_code}] {url} | {title} | {resp.headers.get('server', '')}")
            except Exception as e:
                lines.append(f"[ERR] {url} | {e}")
        return {"ok": True, "output": "\n".join(lines)}
