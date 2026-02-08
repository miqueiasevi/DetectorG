from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

# ===== LOGIN =====
@app.route("/login")
def login():
    return render_template("login.html")

# ===== PÁGINA PRINCIPAL =====
@app.route("/")
def index():
    return render_template("index.html")

# ===== API VERIFICAR LINK =====
@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.get_json()
    link = data.get("link", "")

    if not link:
        return jsonify({
            "status": "erro",
            "resultado": "Link vazio"
        })

    # Simulação (depois liga o DetectorG real)
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

# ⚠️ NÃO DEFINA PORTA NO RENDER
if __name__ == "__main__":
    app.run()
