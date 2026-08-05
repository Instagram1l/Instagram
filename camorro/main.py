import argparse

from .agent import CamorroAgent


def main():
    parser = argparse.ArgumentParser(description="Camorro — مساعد اختبار الاختراق بالذكاء الاصطناعي")
    parser.add_argument("--model", default=None, help="اسم النموذج (مثال: qwen2.5:14b)")
    parser.add_argument("--yes", action="store_true", help="تنفيذ الأوامر بدون تأكيد")
    args = parser.parse_args()

    agent = CamorroAgent(model=args.model, auto_approve=args.yes)
    print("=" * 50)
    print("  🐍 كامورو جاهز! اكتب سؤالك (exit للخروج)")
    print("=" * 50)

    while True:
        try:
            msg = input("\nأنت > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nبسلامة! 👋")
            break
        if not msg:
            continue
        if msg.lower() in ("exit", "quit", "خروج", "سلام"):
            print("بسلامة! 👋")
            break
        print("\nكامورو >", agent.ask(msg))


if __name__ == "__main__":
    main()
