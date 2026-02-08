from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Chave da API Google Safe Browsing (depois podemos trocar por outra)
GOOGLE_API_KEY = "SUA_CHAVE_AQUI"

def check_google_safe_browsing(url):
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_API_KEY}"
    payload = {
        "client": {
            "clientId": "DetectorG",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }

    response = requests.post(endpoint, json=payload)
    if response.status_code == 200 and response.json():
        return True
    return False


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "DetectorG",
        "message": "API funcionando"
    })


@app.route("/check", methods=["GET"])
def check_url():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    is_dangerous = check_google_safe_browsing(url)

    return jsonify({
        "url": url,
        "dangerous": is_dangerous
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
