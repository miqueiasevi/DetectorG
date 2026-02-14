from flask import Flask, render_template, request, jsonify
import json, os, time
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates", static_folder="static")

CODIGOS_FILE = "codigos.json"
USUARIOS_FILE = "usuarios.json"

# =========================
# CARREGAR DADOS
# =========================

def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            return json.load(f)
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w") as f:
        json.dump(dados, f)

codigos = carregar_json(CODIGOS_FILE)
usuarios = carregar_json(USUARIOS_FILE)

# =========================
# HTML
# =========================

@app.route("/pro-system")
def pro_system():
    return render_template("pro-system.html")

# =========================
# CADASTRAR CÓDIGO (AGORA COM TIPO)
# =========================

@app.route("/cadastrar_codigo", methods=["POST"])
def cadastrar_codigo():
    data = request.get_json()
    codigo = data.get("codigo")
    tipo = data.get("tipo")  # individual ou familia

    if not codigo or not tipo:
        return jsonify({"status":"erro","mensagem":"Dados incompletos"})

    if codigo in codigos:
        return jsonify({"status":"erro","mensagem":"Código já existe"})

    codigos[codigo] = {
        "usado": False,
        "criado": int(time.time()),
        "tipo": tipo
    }

    salvar_json(CODIGOS_FILE, codigos)

    return jsonify({"status":"ok"})

# =========================
# VALIDAR CÓDIGO
# =========================

@app.route("/validar_codigo", methods=["POST"])
def validar_codigo():
    data = request.get_json()
    codigo = data.get("codigo")
    usuario = data.get("usuario")

    if not codigo or not usuario:
        return jsonify({"status":"erro","mensagem":"Código ou usuário vazio"})

    if codigo not in codigos:
        return jsonify({"status":"erro","mensagem":"Código inválido"})

    if codigos[codigo]["usado"]:
        return jsonify({"status":"erro","mensagem":"Código já utilizado"})

    # Marca código como usado
    codigos[codigo]["usado"] = True
    salvar_json(CODIGOS_FILE, codigos)

    # Define expiração
    expira_em = datetime.now() + timedelta(days=30)

    usuarios[usuario] = {
        "expira_em": expira_em.isoformat(),
        "tipo_plano": codigos[codigo]["tipo"]
    }

    salvar_json(USUARIOS_FILE, usuarios)

    return jsonify({
        "status":"ok",
        "mensagem":"Plano ativado com sucesso",
        "tipo_plano": codigos[codigo]["tipo"],
        "expira_em": expira_em.strftime("%d/%m/%Y")
    })

# =========================
# VERIFICAR STATUS PRO
# =========================

@app.route("/status_pro", methods=["POST"])
def status_pro():
    data = request.get_json()
    usuario = data.get("usuario")

    if usuario not in usuarios:
        return jsonify({"pro": False})

    expira = datetime.fromisoformat(usuarios[usuario]["expira_em"])

    if datetime.now() < expira:
        return jsonify({
            "pro": True,
            "tipo_plano": usuarios[usuario]["tipo_plano"]
        })

    return jsonify({"pro": False})

# =========================

if __name__ == "__main__":
    app.run()
