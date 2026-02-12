from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import uuid

app = Flask(__name__, template_folder="templates", static_folder="static")

# ===============================
# BANCO SIMPLES EM MEMÓRIA
# (Depois você pode trocar por banco real)
# ===============================

usuarios_pro = {}   # email -> data_expiracao
codigos_pro = {}    # codigo -> usado (True/False)

# ===============================
# ROTAS PRINCIPAIS
# ===============================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

# ===============================
# GERAR CÓDIGO PRO (ADMIN)
# ===============================

@app.route("/gerar_codigo", methods=["POST"])
def gerar_codigo():
    novo_codigo = str(uuid.uuid4()).replace("-", "").upper()[:12]
    codigos_pro[novo_codigo] = False
    return jsonify({
        "status": "ok",
        "codigo": novo_codigo
    })

# ===============================
# ATIVAR PRO
# ===============================

@app.route("/ativar_pro", methods=["POST"])
def ativar_pro():
    data = request.get_json()
    codigo = data.get("codigo")
    email = data.get("email")

    if not codigo or not email:
        return jsonify({
            "status": "erro",
            "mensagem": "Dados inválidos"
        })

    if codigo not in codigos_pro:
        return jsonify({
            "status": "erro",
            "mensagem": "Código inválido"
        })

    if codigos_pro[codigo] is True:
        return jsonify({
            "status": "erro",
            "mensagem": "Código já utilizado"
        })

    # Marca código como usado
    codigos_pro[codigo] = True

    # Ativa PRO por 30 dias
    expiracao = datetime.now() + timedelta(days=30)
    usuarios_pro[email] = expiracao

    return jsonify({
        "status": "ok",
        "expira_em": expiracao.strftime("%d/%m/%Y")
    })

# ===============================
# STATUS PRO
# ===============================

@app.route("/status_pro", methods=["POST"])
def status_pro():
    data = request.get_json()
    email = data.get("email")

    if email in usuarios_pro:
        if datetime.now() < usuarios_pro[email]:
            return jsonify({"pro": True})
        else:
            del usuarios_pro[email]

    return jsonify({"pro": False})

# ===============================
# EXECUÇÃO
# ===============================

if __name__ == "__main__":
    app.run()
