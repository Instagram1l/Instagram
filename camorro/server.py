import argparse

from flask import Flask, jsonify, request, send_from_directory

from .agent import CamorroAgent

app = Flask(__name__, static_folder="../web", static_url_path="")
agent = None


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "اكتب شي حاجة!"}), 400
    reply = agent.ask(msg)
    return jsonify({"reply": reply})


def main():
    global agent
    parser = argparse.ArgumentParser(description="Camorro Web Server")
    parser.add_argument("--model", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--yes", action="store_true", help="تنفيذ الأوامر بدون تأكيد")
    args = parser.parse_args()

    agent = CamorroAgent(model=args.model, auto_approve=args.yes)
    print(f"🌐 كامورو خدام على http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
