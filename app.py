from flask import Flask, render_template, request, jsonify
import json, os, time

app = Flask(__name__, template_folder="templates", static_folder="static")

CODIGOS_FILE = "codigos.json"

# Carrega códigos já salvos
if os.path.exists(CODIGOS_FILE):
    with open(CODIGOS_FILE, "r") as f:
        codigos = json.load(f)
else:
    codigos = {}

# ===== HTML =====
@app.route("/pro-system")
def pro_system():
    return render_template("pro-system.html")

# ===== CADASTRAR CÓDIGO =====
@app.route("/cadastrar_codigo", methods=["POST"])
def cadastrar_codigo():
    data = request.get_json()
    codigo = data.get("codigo")
    if not codigo:
        return jsonify({"status":"erro","mensagem":"Código vazio"})

    if codigo in codigos:
        return jsonify({"status":"erro","mensagem":"Código já existe"})

    codigos[codigo] = {"usado": False, "criado": int(time.time())}
    with open(CODIGOS_FILE, "w") as f:
        json.dump(codigos, f)

    return jsonify({"status":"ok"})

# ===== VALIDAR CÓDIGO =====
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

    codigos[codigo]["usado"] = True
    with open(CODIGOS_FILE, "w") as f:
        json.dump(codigos, f)

    # Aqui você pode ligar para ativar PRO no usuário (DetectorG)
    return jsonify({"status":"ok","mensagem":"Plano PRO ativado por 30 dias"})
