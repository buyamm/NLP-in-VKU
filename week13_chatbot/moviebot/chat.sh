#!/bin/bash
# ============================================================
# chat.sh — Interactive chat shell for Movie Recommendation Bot
#
# Usage:
#   ./chat.sh              # connects to localhost:5005 (default)
#   ./chat.sh 5006         # connects to a custom port
#
# No extra ports needed — talks to the already-running Rasa server
# via its REST API on port 5005.
# ============================================================

PORT=${1:-5005}
URL="http://localhost:${PORT}/webhooks/rest/webhook"

echo ""
echo "🎬  MovieBot Chat Shell"
echo "    Connecting to: ${URL}"
echo "    Type 'quit' or Ctrl+C to exit"
echo "────────────────────────────────────"
echo ""

docker exec -i moviebot_rasa python3 - <<'PYEOF'
import requests, sys, os

url   = os.environ.get("RASA_URL", "http://localhost:5005/webhooks/rest/webhook")
sender = "shell_user"

while True:
    try:
        msg = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBot: Goodbye! 🍿")
        sys.exit(0)

    if not msg:
        continue

    if msg.lower() in ("quit", "exit", "bye", "tạm biệt"):
        try:
            resp = requests.post(url, json={"sender": sender, "message": msg}, timeout=10)
            for r in resp.json():
                print("Bot:", r.get("text", ""))
        except Exception:
            pass
        sys.exit(0)

    try:
        resp = requests.post(url, json={"sender": sender, "message": msg}, timeout=10)
        resp.raise_for_status()
        replies = resp.json()
        if not replies:
            print("Bot: (no response — check action server logs)")
        for r in replies:
            print("Bot:", r.get("text", ""))
    except requests.exceptions.ConnectionError:
        print("Bot: ❌ Cannot connect to Rasa server. Is 'docker compose up' running?")
    except requests.exceptions.Timeout:
        print("Bot: ⏱ Request timed out. Server may be busy.")
    except Exception as e:
        print(f"Bot: ❌ Error — {e}")
PYEOF
