"""
Simple WhatsApp echo bot using Evolution API.

How it works:
1. Evolution API sends a webhook (HTTP POST) to this Flask app whenever
   a message arrives on your connected WhatsApp number.
2. We read the message text out of the webhook payload.
3. We call Evolution API's REST endpoint to send a reply back.

Fill in EVOLUTION_API_URL, API_KEY, and INSTANCE_NAME below.
"""

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ---- CONFIG: fill these in ----
EVOLUTION_API_URL = "https://your-evolution-instance.up.railway.app"
API_KEY = "your-authentication-api-key"   # the AUTHENTICATION_API_KEY you set on Railway
INSTANCE_NAME = "main"                     # the instance name you created in the Manager
# --------------------------------


def send_message(to_number: str, text: str):
    """Send a WhatsApp text message via Evolution API."""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY,
    }
    payload = {
        "number": to_number,
        "text": text,
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Send response:", response.status_code, response.text)
    return response


@app.route("/webhook", methods=["POST"])
def webhook():
    """Evolution API calls this URL whenever a new message arrives."""
    data = request.get_json()
    print("Incoming webhook:", data)

    try:
        message_data = data.get("data", {})
        key = message_data.get("key", {})
        from_number = key.get("remoteJid")  # e.g. "2348012345678@s.whatsapp.net"
        is_from_me = key.get("fromMe", False)

        message_obj = message_data.get("message", {})
        text = message_obj.get("conversation") or message_obj.get("extendedTextMessage", {}).get("text")

        # Don't reply to our own messages (avoid infinite loops!)
        if is_from_me or not text or not from_number:
            return jsonify({"status": "ignored"}), 200

        reply = f"Echo: {text}"
        send_message(from_number, reply)

    except Exception as e:
        print("Error handling webhook:", e)

    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def health():
    return "Bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)