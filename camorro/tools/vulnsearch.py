"""البحث عن الثغرات: قاعدة NVD الرسمية + Exploit-DB المحلي"""
import requests

from ..utils import run_local, check_tool


class VulnSearchTools:
    def cve_search(self, query):
        query = (query or "").strip()
        try:
            r = requests.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={"keywordSearch": query, "resultsPerPage": 15},
                timeout=45,
            )
            if r.status_code != 200:
                return {"ok": False, "output": f"NVD رد برمز {r.status_code}"}
            items = []
            for vuln in r.json().get("vulnerabilities", []):
                cve = vuln["cve"]
                desc = next(
                    (d["value"][:220] for d in cve.get("descriptions", []) if d["lang"] == "en"),
                    "",
                )
                score = ""
                try:
                    score = cve["metrics"]["cvssMetricV31"][0]["cvssData"]["baseScore"]
                except (KeyError, IndexError):
                    pass
                items.append(f"{cve['id']} | CVSS: {score} | {desc}")
            output = "\n".join(items) if items else "لا توجد نتائج مطابقة"
            return {"ok": True, "output": output, "count": len(items)}
        except Exception as e:
            return {"ok": False, "output": f"[!] فشل الاتصال بـ NVD: {e}"}

    def exploit_search(self, query):
        query = (query or "").strip()
        if not check_tool("searchsploit"):
            return {"ok": False, "output": "❌ searchsploit غير مثبت — ثبّت حزمة exploitdb"}
        return run_local(f"searchsploit {query}", timeout=120)
