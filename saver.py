import json

ARQUIVO = "resultados.json"

def salvar_resultado(url, resultado):
    try:
        with open(ARQUIVO, "r") as f:
            dados = json.load(f)
    except:
        dados = []

    dados.append({
        "url": url,
        "score": resultado["score"],
        "nivel": resultado["nivel"],
        "confianca": resultado.get("confianca", 0),
        "riscos": resultado["riscos"]
    })

    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)
