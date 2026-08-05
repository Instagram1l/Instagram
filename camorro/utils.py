"""دوال مساعدة مشتركة: تنفيذ أوامر، تحليل مخرجات، إصلاح JSON"""
import json
import re
import shutil
import subprocess
from pathlib import Path


def run_local(command, timeout=1800, cwd=None):
    """تنفيذ أمر محلي وإرجاع نتيجة منظمة"""
    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd, capture_output=True,
            text=True, timeout=timeout, executable="/bin/bash",
        )
        output = (result.stdout or "") + (result.stderr or "")
        return {
            "ok": result.returncode == 0,
            "output": output.strip()[:32000],
            "code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": f"[!] انتهت المهلة ({timeout}s)"}
    except Exception as e:
        return {"ok": False, "output": f"[!] خطأ في التنفيذ: {e}"}


def check_tool(name):
    """هل الأداة مثبتة على النظام؟"""
    return shutil.which(name) is not None


def parse_nmap_services(text):
    """استخراج جدول المنافذ المفتوحة من مخرجات nmap"""
    services = []
    for line in text.splitlines():
        m = re.match(r"^(\d+)/tcp\s+open\s+(\S+)\s+(.*)$", line.strip())
        if m:
            services.append({
                "port": m.group(1),
                "service": m.group(2),
                "detail": m.group(3).strip(),
            })
    return services


def extract_json(text):
    """محاولة استخراج JSON صالح من نص — لإصلاح وسائط الأدوات"""
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def strip_thinking(text):
    """إزالة وسوم التفكير الداخلية (deepseek-r1 وغيرها)"""
    return re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()
