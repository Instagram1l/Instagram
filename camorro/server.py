"""خادم الويب (Flask) — واجهة عربية RTL"""
import argparse
import os

from flask import Flask, jsonify, request, send_from_directory

from .agent import CamorroAgent

app = Flask(__name__, static_folder="../web", static_url_path="")
agent = None


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "model": agent.llm.model if agent else None,
        "unrestricted": agent.executor.unrestricted if agent else False,
        "workspace": str(agent.executor.workspace) if agent else None,
    })


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "اكتب شي حاجة!"}), 400
    try:
        reply = agent.ask(msg)
    except Exception as e:
        reply = f"⚠️ خطأ داخلي: {e}"
    return jsonify({"reply": reply})


def main():
    global agent
    parser = argparse.ArgumentParser(description="كامورو — خادم الويب")
    parser.add_argument("--model", default=os.getenv("CAMORRO_MODEL"))
    parser.add_argument("--llm-url", default=os.getenv("CAMORRO_LLM_URL"))
    parser.add_argument("--api-key", default=os.getenv("CAMORRO_API_KEY"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--yes", action="store_true", help="تنفيذ بدون تأكيد")
    parser.add_argument("--unrestricted", action="store_true",
                        help="🔥 الوضع الكامل بدون قيود")
    parser.add_argument("--iterations", type=int, default=40)
    parser.add_argument("--workspace", default="workspace")
    args = parser.parse_args()

    agent = CamorroAgent(
        model=args.model, llm_url=args.llm_url, api_key=args.api_key,
        auto_approve=args.yes, unrestricted=args.unrestricted,
        max_iterations=args.iterations, workspace=args.workspace,
    )
    mode = "UNRESTRICTED 🔥" if args.unrestricted else "عادي (مع حماية)"
    print(f"🌐 كامورو خدام على http://{args.host}:{args.port}")
    print(f"🤖 النموذج: {agent.llm.model} | الوضع: {mode}")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
