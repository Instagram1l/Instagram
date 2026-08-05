"""حلقة التفكير: نموذج ← أدوات ← تحليل ← رد، مع إدارة سياق ذكية"""
import json

from .llm import LLMClient
from .prompts import SYSTEM_PROMPT, TOOLS
from .tools import ToolExecutor
from .utils import extract_json, strip_thinking


class CamorroAgent:
    def __init__(self, model=None, auto_approve=False, unrestricted=False,
                 max_iterations=40, workspace=None, llm_url=None, api_key=None):
        self.llm = LLMClient(base_url=llm_url, model=model, api_key=api_key)
        self.executor = ToolExecutor(
            auto_approve=auto_approve,
            unrestricted=unrestricted,
            workspace=workspace,
        )
        self.max_iterations = max_iterations
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def ask(self, user_msg):
        self.history.append({"role": "user", "content": user_msg})
        last_reply = ""

        for _ in range(self.max_iterations):
            try:
                resp = self.llm.chat(self.history, tools=TOOLS)
            except Exception as e:
                last_reply = f"⚠️ فشل الاتصال بالنموذج: {e}"
                break

            msg = resp.get("message", {})
            content = strip_thinking(msg.get("content") or "")
            tool_calls = msg.get("tool_calls") or []

            if content and not tool_calls:
                last_reply = content

            self.history.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": tool_calls or None,
            })

            if not tool_calls:
                break  # النموذج جاوب — انتهت الجولة

            for tc in tool_calls:
                fn = tc.get("function", {}).get("name", "")
                raw = tc.get("function", {}).get("arguments") or "{}"
                args = extract_json(raw) if isinstance(raw, str) else raw
                if not isinstance(args, dict):
                    args = {}

                try:
                    handler = getattr(self.executor, fn, None)
                    if handler is None:
                        result = {"ok": False, "output": f"أداة غير معروفة: {fn}"}
                    else:
                        result = handler(**args)
                except TypeError as e:
                    result = {"ok": False, "output": f"[!] وسائط خاطئة لـ {fn}: {e}"}
                except Exception as e:
                    result = {"ok": False, "output": f"[!] فشل تنفيذ {fn}: {e}"}

                self.history.append({
                    "role": "tool",
                    "name": fn,
                    "content": json.dumps(result, ensure_ascii=False)[:16000],
                })

            # منع تضخم السياق: احتفظ بالنظام + آخر 30 رسالة
            if len(self.history) > 40:
                self.history = self.history[:1] + self.history[-30:]

        return last_reply or "⚠️ لم أصل لجواب — جرّب إعادة الصياغة أو زد --iterations"
