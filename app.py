import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
import uuid

app = Flask(__name__, template_folder="templates", static_folder="static")

DATABASE = "database.db"

# =============================
# CRIAR BANCO
# =============================

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS codigos_pro (
        codigo TEXT PRIMARY KEY,
        usado INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_pro (
        email TEXT PRIMARY KEY,
        expira_em TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =============================
# ROTAS
# =============================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

# =============================
# GERAR CÓDIGO (ADMIN)
# =============================

@app.route("/gerar_codigo", methods=["POST"])
def gerar_codigo():
    codigo = str(uuid.uuid4()).replace("-", "").upper()[:12]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO codigos_pro (codigo, usado) VALUES (?, ?)",
        (codigo, 0)
    )

    conn.commit()
    conn.close()

    return jsonify({"codigo": codigo})

# =============================
# ATIVAR PRO
# =============================

@app.route("/ativar_pro", methods=["POST"])
def ativar_pro():
    data = request.get_json()
    codigo = data.get("codigo")
    email = data.get("email")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT usado FROM codigos_pro WHERE codigo = ?",
        (codigo,)
    )
    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return jsonify({"status": "erro", "mensagem": "Código inválido"})

    if resultado[0] == 1:
        conn.close()
        return jsonify({"status": "erro", "mensagem": "Código já utilizado"})

    # Marca como usado
    cursor.execute(
        "UPDATE codigos_pro SET usado = 1 WHERE codigo = ?",
        (codigo,)
    )

    expira_em = datetime.now() + timedelta(days=30)

    cursor.execute("""
        INSERT OR REPLACE INTO usuarios_pro (email, expira_em)
        VALUES (?, ?)
    """, (email, expira_em.isoformat()))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok",
        "expira_em": expira_em.strftime("%d/%m/%Y")
    })

# =============================
# VERIFICAR STATUS PRO
# =============================

@app.route("/status_pro", methods=["POST"])
def status_pro():
    data = request.get_json()
    email = data.get("email")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT expira_em FROM usuarios_pro WHERE email = ?",
        (email,)
    )
    resultado = cursor.fetchone()

    conn.close()

    if resultado:
        expira = datetime.fromisoformat(resultado[0])
        if datetime.now() < expira:
            return jsonify({"pro": True})

    return jsonify({"pro": False})

# =============================

if __name__ == "__main__":
    app.run()
