import json

from .llm import LLMClient
from .prompts import SYSTEM_PROMPT, TOOLS
from .tools import ToolExecutor


class CamorroAgent:
    """حلقة التفكير: يسأل النموذج ← ينفذ الأدوات ← يحلل ← يرد"""

    def __init__(self, model=None, auto_approve=False):
        self.llm = LLMClient(model=model)
        self.executor = ToolExecutor(auto_approve=auto_approve)
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def ask(self, user_msg):
        self.history.append({"role": "user", "content": user_msg})
        last_reply = ""

        for _ in range(12):  # حد أقصى: 12 استدعاء أداة في الجولة
            resp = self.llm.chat(self.history, tools=TOOLS)
            msg = resp["message"]
            content = msg.get("content") or ""
            tool_calls = msg.get("tool_calls") or []

            if content and not tool_calls:
                last_reply = content

            self.history.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": tool_calls or None,
            })

            if not tool_calls:
                break  # النموذج جاوب — خلاص

            for tc in tool_calls:
                fn = tc["function"]["name"]
                raw_args = tc["function"].get("arguments") or "{}"
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        args = {}
                else:
                    args = raw_args
                if not isinstance(args, dict):
                    args = {}

                result = getattr(self.executor, fn)(**args)
                self.history.append({
                    "role": "tool",
                    "name": fn,
                    "content": json.dumps(result, ensure_ascii=False)[:16000],
                })

        return last_reply or "(كامورو ما قدرش يجاوب — جرب تعيد الصياغة)"
