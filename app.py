from flask import Flask, render_template, request, jsonify
import json, os, time
from datetime import datetime, timedelta
from deep_analysis import deep_scan  # ✅ Importa análise avançada PRO

app = Flask(__name__, template_folder="templates", static_folder="static")

CODIGOS_FILE = "codigos.json"
USUARIOS_FILE = "usuarios.json"

# =========================
# FUNÇÕES DE JSON
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

# =========================
# CADASTRAR CÓDIGO
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

    codigos[codigo] = {"usado": False, "criado": int(time.time()), "tipo": tipo}
    salvar_json(CODIGOS_FILE, codigos)

    return jsonify({"status":"ok","mensagem":"Código cadastrado com sucesso"})

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

    # Define expiração e tipo do plano
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
            "tipo_plano": usuarios[usuario]["tipo_plano"],
            "expira_em": expira.strftime("%d/%m/%Y")
        })

    return jsonify({"pro": False})

# =========================
# VERIFICAR LINK
# =========================
def basic_scan(link):
    """Análise básica gratuita"""
    url = link.lower()
    riscos = []
    score = 0

    # PHISHING
    phishing = ["login","verify","secure","account","update",".xyz",".top",".tk",".info"]
    for p in phishing:
        if p in url:
            riscos.append("Phishing")
            score += 30

    # DRIVE-BY DOWNLOAD
    downloads = [".exe",".apk",".msi",".zip",".rar"]
    for d in downloads:
        if d in url:
            riscos.append("Drive-by Download")
            score += 50

    nivel = "🟢 Baixo"
    if score >= 30: nivel = "🟡 Médio"
    if score >= 70: nivel = "🔴 Alto"

    return {"nivel": nivel, "riscos": riscos}

@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.get_json()
    link = data.get("link")
    usuario = data.get("usuario")

    if not link or not usuario:
        return jsonify({"status":"erro","mensagem":"Link ou usuário vazio"})

    # Busca se usuário é PRO
    pro_status = usuarios.get(usuario, {}).get("tipo_plano")
    if pro_status:
        resultado = deep_scan(link)      # análise avançada PRO
    else:
        resultado = basic_scan(link)     # análise básica gratuita

    return jsonify({"status":"ok", "resultado": resultado})

# =========================
# RODAR APP
# =========================
if __name__ == "__main__":
    app.run()
