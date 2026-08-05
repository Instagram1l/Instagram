"""الواجهة الطرفية (CLI) — كامورو"""
import argparse
import os

from .agent import CamorroAgent

BANNER = r"""
   ___                              ___
  / __|__ _ _ _ _ _  _ _ __ ___ _ _| _ \__ _ _ _
 | (__/ _` | '_| ' \| '_/ _/ _ \ '_|   / _` | '_|
  \___\__,_|_| |_||_|_| \__\___/_| |_|_\__,_|_|
"""


def main():
    parser = argparse.ArgumentParser(
        description="كامورو — وكيل اختبار الاختراق بالذكاء الاصطناعي (محلي 100%)"
    )
    parser.add_argument("--model", default=os.getenv("CAMORRO_MODEL"),
                        help="اسم النموذج (افتراضي: dolphin-llama3:8b)")
    parser.add_argument("--llm-url", default=os.getenv("CAMORRO_LLM_URL"),
                        help="رابط Ollama أو خادم OpenAI")
    parser.add_argument("--api-key", default=os.getenv("CAMORRO_API_KEY"),
                        help="مفتاح API لخوادم OpenAI")
    parser.add_argument("--yes", action="store_true",
                        help="تنفيذ الأوامر بدون تأكيد")
    parser.add_argument("--unrestricted", action="store_true",
                        help="🔥 الوضع الكامل: بدون أي قيود أو حجب")
    parser.add_argument("--iterations", type=int, default=40,
                        help="حد استدعاءات الأدوات بالجولة")
    parser.add_argument("--workspace", default="workspace",
                        help="مجلد العمل (الافتراضي: workspace)")
    args = parser.parse_args()

    agent = CamorroAgent(
        model=args.model, llm_url=args.llm_url, api_key=args.api_key,
        auto_approve=args.yes, unrestricted=args.unrestricted,
        max_iterations=args.iterations, workspace=args.workspace,
    )

    mode = "UNRESTRICTED 🔥" if args.unrestricted else "عادي (مع حماية)"
    print(BANNER)
    print("=" * 52)
    print(f"  🐍 كامورو v2.0 جاهز!  الوضع: {mode}")
    print(f"  🤖 النموذج: {agent.llm.model}")
    print(f"  💬 اكتب سؤالك (exit / خروج للخروج)")
    print("=" * 52)

    while True:
        try:
            msg = input("\nأنت > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 بسلامة!")
            break
        if not msg:
            continue
        if msg.lower() in ("exit", "quit", "خروج", "سلام", "q"):
            print("👋 بسلامة!")
            break
        print("\nكامورو > ", end="", flush=True)
        print(agent.ask(msg))


if __name__ == "__main__":
    main()
