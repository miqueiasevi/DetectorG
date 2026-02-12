from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "super_secret_key_detectorg"

# =========================
# BANCO DE DADOS
# =========================

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS codigos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        usado INTEGER DEFAULT 0,
        data_ativacao TEXT,
        data_expiracao TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# LOGIN
# =========================

@app.route("/login")
def login():
    return render_template("login.html")

# =========================
# HOME
# =========================

@app.route("/")
def index():
    return render_template("index.html")

# =========================
# ATIVAR PRO
# =========================

@app.route("/ativar_pro", methods=["POST"])
def ativar_pro():
    data = request.get_json()
    codigo = data.get("codigo", "").strip()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT usado FROM codigos WHERE codigo = ?", (codigo,))
    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return jsonify({"status": "erro", "mensagem": "Código inválido"})

    if resultado[0] == 1:
        conn.close()
        return jsonify({"status": "erro", "mensagem": "Código já utilizado"})

    # Ativar código
    data_ativacao = datetime.now()
    data_expiracao = data_ativacao + timedelta(days=30)

    cursor.execute("""
        UPDATE codigos
        SET usado = 1,
            data_ativacao = ?,
            data_expiracao = ?
        WHERE codigo = ?
    """, (data_ativacao.isoformat(), data_expiracao.isoformat(), codigo))

    conn.commit()
    conn.close()

    session["pro"] = True
    session["expira"] = data_expiracao.isoformat()

    return jsonify({"status": "ok", "mensagem": "Plano PRO ativado por 30 dias"})

# =========================
# VERIFICAR LINK
# =========================

@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.get_json()
    link = data.get("link", "")

    if not link:
        return jsonify({
            "status": "erro",
            "resultado": "Link vazio"
        })

    # Verifica se usuário é PRO
    if "pro" not in session:
        return jsonify({
            "status": "erro",
            "resultado": "Recurso disponível apenas para usuários PRO"
        })

    # Verifica expiração
    expira = datetime.fromisoformat(session["expira"])
    if datetime.now() > expira:
        session.clear()
        return jsonify({
            "status": "erro",
            "resultado": "Plano PRO expirado"
        })

    # Simulação
    if link.startswith("http"):
        return jsonify({
            "status": "ok",
            "resultado": "Link aparentemente seguro"
        })
    else:
        return jsonify({
            "status": "alerta",
            "resultado": "Link suspeito"
        })

# =========================
# GERAR CÓDIGO (ADMIN)
# =========================

@app.route("/gerar_codigo")
def gerar_codigo():
    novo_codigo = f"PRO-{datetime.now().timestamp()}"

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO codigos (codigo) VALUES (?)", (novo_codigo,))
    conn.commit()
    conn.close()

    return jsonify({"codigo": novo_codigo})


# ⚠️ NÃO DEFINA PORTA NA RENDER
if __name__ == "__main__":
    app.run()
