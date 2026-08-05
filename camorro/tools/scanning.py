"""أدوات الفحص: nmap + fuzzing مسارات"""
from ..utils import run_local, check_tool, parse_nmap_services


class ScanningTools:
    def nmap_scan(self, target, ports="", aggressive=False):
        target = (target or "").strip()
        if not check_tool("nmap"):
            return {"ok": False, "output": "❌ nmap غير مثبت"}
        cmd = "nmap -sV -sC --open -Pn"
        if ports:
            cmd += f" -p {ports}"
        if aggressive:
            cmd += " -A -p- --min-rate 1000"
        cmd += f" {target}"
        r = run_local(cmd, timeout=1800)
        r["services"] = parse_nmap_services(r["output"])
        if r["services"]:
            summary = "\n".join(
                f"  ⚡ {s['port']}/tcp  {s['service']}  {s['detail']}"
                for s in r["services"]
            )
            r["output"] += f"\n\n✅ منافذ مفتوحة ({len(r['services'])}):\n{summary}"
        return r

    def dir_fuzz(self, url, wordlist="", extensions=""):
        url = (url or "").strip()
        if not check_tool("ffuf"):
            return {"ok": False, "output": "❌ ffuf غير مثبت — شغّل install_tools.sh"}
        wl = wordlist or "/usr/share/wordlists/dirb/common.txt"
        cmd = f"ffuf -u {url} -w {wl} -mc 200,204,301,302,307,401,403 -t 50"
        if extensions:
            ext = extensions.replace(",", ",.").strip()
            if not ext.startswith("."):
                ext = "." + ext
            cmd += f" -e {ext}"
        r = run_local(cmd, timeout=1800)
        found = [l for l in r["output"].splitlines() if "|" in l and "FUZZ" not in l]
        r["found"] = found
        if found:
            r["output"] += f"\n\n✅ مسارات مكتشفة ({len(found)}):\n" + "\n".join(found)
        return r
