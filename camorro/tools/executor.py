import subprocess
from pathlib import Path

# أوامر خطيرة ممنوعة تلقائيًا (حماية للنظام)
DANGEROUS = ["rm -rf /", "mkfs", "dd if=", "> /dev/sd", ":(){", "shutdown", "reboot", "chmod -R 777 /"]


class ToolExecutor:
    """تنفيذ الأدوات الأمنية مع مساحة عمل آمنة"""

    def __init__(self, auto_approve=False, workspace=None):
        self.auto_approve = auto_approve
        self.workspace = Path(workspace or "workspace").resolve()
        self.workspace.mkdir(exist_ok=True)

    def run_command(self, command):
        if any(p in command for p in DANGEROUS) and not self.auto_approve:
            return {"ok": False, "output": f"[⛔] أمر خطير ممنوع: {command}"}
        try:
            result = subprocess.run(command, shell=True, cwd=self.workspace,
                                    capture_output=True, text=True, timeout=600)
            output = (result.stdout + result.stderr).strip()
            return {"ok": result.returncode == 0, "output": output[:8000],
                    "code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": "[!] انتهى الوقت (timeout 600s)"}
        except Exception as e:
            return {"ok": False, "output": f"[!] خطأ: {e}"}

    def read_file(self, path):
        p = (self.workspace / path).resolve()
        if not p.exists():
            return {"ok": False, "output": f"الملف غير موجود: {path}"}
        return {"ok": True, "output": p.read_text(errors="replace")[:8000]}

    def write_file(self, path, content):
        p = (self.workspace / path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"ok": True, "output": f"✅ تم حفظ الملف: {path}"}
