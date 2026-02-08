from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

# Verificação de link (simulação por enquanto)
@app.route("/verificar", methods=["POST"])
def verificar():
    data = request.json
    link = data.get("link", "")

    if not link:
        return jsonify({"status": "erro", "mensagem": "Link vazio"})

    # Aqui depois você liga o DetectorG real
    if "http" in link:
        return jsonify({
            "status": "ok",
            "resultado": "Link aparentemente seguro"
        })
    else:
        return jsonify({
            "status": "alerta",
            "resultado": "Link suspeito"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8800)
