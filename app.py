from flask import Flask, render_template, request, jsonify
import json, os, time, re, requests, uuid
from datetime import datetime, timedelta
from deep_analysis import deep_scan

app = Flask(__name__, template_folder="templates", static_folder="static")

CODIGOS_FILE = "codigos.json"
USUARIOS_FILE = "usuarios.json"
LOGS_FILE = "logs.json"

# 🔥 TOKEN (usa variável do Render ou coloca direto)
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN") or "COLE_SEU_TOKEN_AQUI"

# =========================
# SEGURANÇA
# =========================

def limpar_input(texto):
    if not texto:
        return ""
    return re.sub(r"[<>\"'%;()&+]", "", texto)

def log_evento(msg):
    logs = carregar_json(LOGS_FILE)
    logs[str(time.time())] = msg
    salvar_json(LOGS_FILE, logs)

def usuario_existe(usuario):
    return usuario in usuarios

# =========================
# JSON
# =========================

def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            return json.load(f)
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w") as f:
        json.dump(dados, f, indent=4)

codigos = carregar_json(CODIGOS_FILE)
usuarios = carregar_json(USUARIOS_FILE)

# =========================
# ROTA PRINCIPAL
# =========================

@app.route("/")
def index():
    return render_template("index.html")

# =========================
# 🔥 PAGAMENTO PIX (CORRIGIDO)
# =========================

@app.route("/criar_pagamento", methods=["POST"])
def criar_pagamento():

    if not MP_ACCESS_TOKEN or "COLE_SEU_TOKEN_AQUI" in MP_ACCESS_TOKEN:
        return jsonify({
            "status":"erro",
            "mensagem":"TOKEN DO MERCADO PAGO NÃO CONFIGURADO"
        })

    data = request.get_json(silent=True) or {}
    usuario = limpar_input(data.get("usuario"))

    if not usuario:
        return jsonify({"status":"erro","mensagem":"Usuário inválido"})

    url = "https://api.mercadopago.com/v1/payments"

    headers = {
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4())  # 🔥 ESSENCIAL
    }

    payload = {
        "transaction_amount": 9.90,
        "description": "Plano PRO DetectorG",
        "payment_method_id": "pix",
        "payer": {
            "email": f"{usuario}@detectorg.com"
        },
        "external_reference": usuario
    }

    try:
        resposta = requests.post(url, json=payload, headers=headers)
        pagamento = resposta.json()

        print("RESPOSTA MERCADO PAGO:")
        print(pagamento)

        # 🔥 SE DER ERRO NA API
        if "point_of_interaction" not in pagamento:
            return jsonify({
                "status":"erro",
                "mensagem":"Erro ao gerar PIX",
                "debug": pagamento
            })

        qr = pagamento["point_of_interaction"]["transaction_data"]["qr_code"]
        qr_base64 = pagamento["point_of_interaction"]["transaction_data"]["qr_code_base64"]

        return jsonify({
            "status":"ok",
            "pix": qr,
            "qr_code_base64": qr_base64
        })

    except Exception as e:
        print("ERRO PAGAMENTO:", str(e))
        return jsonify({
            "status":"erro",
            "mensagem": str(e)
        })

# =========================
# WEBHOOK
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    try:
        if data.get("type") == "payment":
            payment_id = data["data"]["id"]

            url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
            headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}

            resposta = requests.get(url, headers=headers)
            pagamento = resposta.json()

            if pagamento.get("status") == "approved":
                usuario = pagamento.get("external_reference")

                if usuario:
                    expira_em = datetime.now() + timedelta(days=30)

                    usuarios[usuario] = {
                        "expira_em": expira_em.isoformat(),
                        "tipo_plano": "pro",
                        "uso_hoje": 0,
                        "ultimo_dia": datetime.now().strftime("%Y-%m-%d")
                    }

                    salvar_json(USUARIOS_FILE, usuarios)
                    log_evento(f"Pagamento aprovado: {usuario}")

    except Exception as e:
        log_evento(f"Erro webhook: {str(e)}")

    return jsonify({"status":"ok"})

# =========================
# STATUS
# =========================

@app.route("/status_pro", methods=["POST"])
def status_pro():
    data = request.get_json(silent=True) or {}
    usuario = limpar_input(data.get("usuario"))

    if usuario not in usuarios:
        return jsonify({"pro": False})

    expira = datetime.fromisoformat(usuarios[usuario]["expira_em"])

    if datetime.now() < expira:
        return jsonify({
            "pro": True,
            "expira_em": expira.strftime("%d/%m/%Y")
        })

    return jsonify({"pro": False})

# =========================
# SCAN
# =========================

def basic_scan(link):
    url = link.lower()
    riscos = []
    score = 0

    if any(p in url for p in ["login","verify","secure","account",".xyz",".tk",".top"]):
        riscos.append("Phishing")
        score += 30

    if any(d in url for d in [".exe",".apk",".zip",".rar",".msi"]):
        riscos.append("Malware")
        score += 50

    nivel = "🟢 Baixo"
    if score >= 30: nivel = "🟡 Médio"
    if score >= 70: nivel = "🔴 Alto"

    return {
        "nivel": nivel,
        "riscos": riscos
    }

@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.get_json(silent=True) or {}

    link = limpar_input(data.get("link"))
    usuario = limpar_input(data.get("usuario"))

    if not link or not usuario:
        return jsonify({"status":"erro","mensagem":"Dados inválidos"})

    if not usuario_existe(usuario):
        usuarios[usuario] = {
            "expira_em": datetime.now().isoformat(),
            "tipo_plano": "free",
            "uso_hoje": 0,
            "ultimo_dia": datetime.now().strftime("%Y-%m-%d")
        }

    user = usuarios[usuario]
    hoje = datetime.now().strftime("%Y-%m-%d")

    if user.get("ultimo_dia") != hoje:
        user["uso_hoje"] = 0
        user["ultimo_dia"] = hoje

    if user.get("tipo_plano") != "pro":

        if user.get("uso_hoje", 0) >= 3:
            return jsonify({
                "status": "erro",
                "mensagem": "Limite diário atingido"
            })

        user["uso_hoje"] += 1
        resultado = basic_scan(link)

    else:
        resultado = deep_scan(link)

    salvar_json(USUARIOS_FILE, usuarios)

    return jsonify({
        "status":"ok",
        "resultado": resultado,
        "restantes": 3 - user.get("uso_hoje", 0) if user.get("tipo_plano") != "pro" else "ilimitado"
    })

# =========================
# START
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
