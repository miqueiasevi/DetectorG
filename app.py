from flask import Flask, render_template, request, jsonify
import json, os, time, re
from datetime import datetime, timedelta
from deep_analysis import deep_scan

app = Flask(__name__, template_folder="templates", static_folder="static")

CODIGOS_FILE = "codigos.json"
USUARIOS_FILE = "usuarios.json"
LOGS_FILE = "logs.json"

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
# ROTAS HTML
# =========================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/pro-system")
def pro_system():
    return render_template("pro-system.html")

@app.route("/resultado")
def resultado():
    return render_template("resultado.html")

# =========================
# CADASTRAR CÓDIGO
# =========================

@app.route("/cadastrar_codigo", methods=["POST"])
def cadastrar_codigo():
    data = request.get_json()

    codigo = limpar_input(data.get("codigo"))
    tipo = limpar_input(data.get("tipo"))

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
    log_evento(f"Código criado: {codigo}")

    return jsonify({"status":"ok","mensagem":"Código criado"})

# =========================
# VALIDAR CÓDIGO
# =========================

@app.route("/validar_codigo", methods=["POST"])
def validar_codigo():
    data = request.get_json()

    codigo = limpar_input(data.get("codigo"))
    usuario = limpar_input(data.get("usuario"))

    if not codigo or not usuario:
        return jsonify({"status":"erro","mensagem":"Dados inválidos"})

    if codigo not in codigos:
        return jsonify({"status":"erro","mensagem":"Código inválido"})

    if codigos[codigo]["usado"]:
        return jsonify({"status":"erro","mensagem":"Código já usado"})

    codigos[codigo]["usado"] = True
    salvar_json(CODIGOS_FILE, codigos)

    expira_em = datetime.now() + timedelta(days=30)

    usuarios[usuario] = {
        "expira_em": expira_em.isoformat(),
        "tipo_plano": codigos[codigo]["tipo"]
    }

    salvar_json(USUARIOS_FILE, usuarios)
    log_evento(f"{usuario} ativou plano {codigos[codigo]['tipo']}")

    return jsonify({
        "status":"ok",
        "mensagem":"Plano ativado",
        "tipo_plano": codigos[codigo]["tipo"],
        "expira_em": expira_em.strftime("%d/%m/%Y")
    })

# =========================
# STATUS PRO
# =========================

@app.route("/status_pro", methods=["POST"])
def status_pro():
    data = request.get_json()
    usuario = limpar_input(data.get("usuario"))

    if usuario not in usuarios:
        return jsonify({"pro": False})

    expira = datetime.fromisoformat(usuarios[usuario]["expira_em"])

    if datetime.now() < expira:
        return jsonify({
            "pro": True,
            "tipo_plano": usuarios[usuario]["tipo_plano"],
            "expira_em": expira.strftime("%d/%m/%Y")
        })

    return jsonify({"pro": False})

# =========================
# ANÁLISE BÁSICA (FREE)
# =========================

def basic_scan(link):
    url = link.lower()
    riscos = []
    score = 0

    # PHISHING
    if any(p in url for p in ["login","verify","secure","account",".xyz",".tk",".top"]):
        riscos.append("Phishing")
        score += 30

    # DOWNLOAD MALICIOSO
    if any(d in url for d in [".exe",".apk",".zip",".rar",".msi"]):
        riscos.append("Drive-by Download")
        score += 50

    nivel = "🟢 Baixo"
    if score >= 30: nivel = "🟡 Médio"
    if score >= 70: nivel = "🔴 Alto"

    return {
        "modo": "FREE",
        "nivel": nivel,
        "score": score,
        "riscos": riscos
    }

# =========================
# VERIFICAR LINK
# =========================

@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.get_json()

    link = limpar_input(data.get("link"))
    usuario = limpar_input(data.get("usuario"))

    if not link or not usuario:
        return jsonify({"status":"erro","mensagem":"Dados inválidos"})

    if not usuario_existe(usuario):
        return jsonify({"status":"erro","mensagem":"Usuário inválido"})

    pro_status = usuarios.get(usuario, {}).get("tipo_plano")

    if pro_status:
        resultado = deep_scan(link)  # PRO 🔥
    else:
        resultado = basic_scan(link)  # FREE

    log_evento(f"{usuario} analisou {link}")

    return jsonify({
        "status":"ok",
        "resultado": resultado
    })

# =========================
# INICIAR
# =========================

if __name__ == "__main__":
    app.run()
