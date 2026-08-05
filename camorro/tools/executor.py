"""المنفذ الأساسي: أوامر + ملفات مع نظام حماية مزدوج"""
from pathlib import Path

from ..utils import run_local

# أنماط تدمير النظام — تُمنع في الوضع العادي فقط
DANGEROUS_PATTERNS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=", "> /dev/sd", ":(){",
    "shutdown", "reboot", "chmod -R 777 /", "chown -R", "fdisk",
    "mkswap", "> /dev/sda", "halt", "poweroff", "format c:",
]


class BaseExecutor:
    def __init__(self, auto_approve=False, unrestricted=False, workspace=None):
        self.auto_approve = auto_approve
        self.unrestricted = unrestricted
        self.workspace = Path(workspace or "workspace").resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    # ---------- تنفيذ الأوامر ----------
    def run_command(self, command):
        command = (command or "").strip()
        if not command:
            return {"ok": False, "output": "أمر فارغ"}
        # الوضع العادي فقط: منع الأوامر المدمرة
        if not self.unrestricted and not self.auto_approve:
            for bad in DANGEROUS_PATTERNS:
                if bad in command:
                    return {
                        "ok": False,
                        "output": f"[⛔] ممنوع في الوضع العادي: {bad}\n"
                                  "شغّل مع --unrestricted للتنفيذ الكامل",
                    }
        return run_local(command, cwd=str(self.workspace))

    # ---------- الملفات ----------
    def _resolve_path(self, path):
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace / p
        p = p.resolve()
        if not self.unrestricted:
            if not str(p).startswith(str(self.workspace)):
                raise PermissionError(f"خارج مساحة العمل: {path}")
        return p

    def read_file(self, path):
        try:
            p = self._resolve_path(path)
            if not p.exists():
                return {"ok": False, "output": f"الملف غير موجود: {path}"}
            content = p.read_text(encoding="utf-8", errors="replace")
            return {"ok": True, "output": content[:32000], "size": len(content)}
        except Exception as e:
            return {"ok": False, "output": f"[!] {e}"}

    def write_file(self, path, content):
        try:
            p = self._resolve_path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content or "", encoding="utf-8")
            return {"ok": True, "output": f"✅ حُفظ الملف: {p}", "path": str(p)}
        except Exception as e:
            return {"ok": False, "output": f"[!] {e}"}
