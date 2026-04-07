import json
from urllib.parse import urlparse

ARQUIVO_DB = "database.json"

def carregar_db():
    try:
        with open(ARQUIVO_DB, "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_db(db):
    with open(ARQUIVO_DB, "w") as f:
        json.dump(db, f, indent=4)

def registrar_scan(url, resultado):
    db = carregar_db()

    dominio = urlparse(url).netloc

    if dominio not in db:
        db[dominio] = {
            "visitas": 1,
            "scores": [resultado["score"]],
            "riscos": resultado["riscos"]
        }
    else:
        db[dominio]["visitas"] += 1
        db[dominio]["scores"].append(resultado["score"])

    salvar_db(db)
