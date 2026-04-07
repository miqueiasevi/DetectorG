import re
import math
import json
import os
from urllib.parse import urlparse

# =========================
# 📂 BANCO DE REPUTAÇÃO (AUTO APRENDIZADO)
# =========================

DB_FILE = "reputacao.json"

def carregar_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

# =========================
# BASE LOCAL
# =========================

BLACKLIST_DOMINIOS = [
    "phishing.com",
    "malware-site.net",
    "fakebank.xyz",
    "login-secure-fake.com"
]

BLACKLIST_IPS = [
    "192.168.1.100",
    "10.0.0.5"
]

DOMINIOS_SUSPEITOS = [".xyz", ".tk", ".top", ".gq", ".ml"]

ENCURTADORES = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly"]

MARCAS = ["google", "facebook", "paypal", "instagram", "bank"]

# =========================
# 🔬 ENTROPIA
# =========================
def calcular_entropia(texto):
    if len(texto) < 5:
        return 0
    prob = [float(texto.count(c)) / len(texto) for c in set(texto)]
    return -sum([p * math.log2(p) for p in prob])

# =========================
# 🚀 FUNÇÃO PRINCIPAL
# =========================
def check_threat_intel(url):
    riscos = []
    score = 0

    db = carregar_db()

    dominio = urlparse(url).netloc.lower()

    # =========================
    # 🔴 BLACKLIST
    # =========================
    if dominio in BLACKLIST_DOMINIOS:
        riscos.append("Domínio em blacklist")
        score += 90

    # =========================
    # 🌍 REPUTAÇÃO (AUTO APRENDIZADO)
    # =========================
    if dominio in db:
        rep = db[dominio]
        score += rep * 0.6  # peso inteligente

        if rep > 50:
            riscos.append("Má reputação histórica")

    # =========================
    # 🔴 IP DIRETO
    # =========================
    if re.match(r"\d+\.\d+\.\d+\.\d+", dominio):
        if dominio in BLACKLIST_IPS:
            riscos.append("IP malicioso conhecido")
            score += 95
        else:
            riscos.append("Uso de IP direto")
            score += 50

    # =========================
    # 🟠 TLD SUSPEITO
    # =========================
    if any(dominio.endswith(tld) for tld in DOMINIOS_SUSPEITOS):
        riscos.append("TLD suspeito")
        score += 20

    # =========================
    # 🟠 URL ENCURTADA
    # =========================
    if any(short in dominio for short in ENCURTADORES):
        riscos.append("URL encurtada")
        score += 25

    # =========================
    # 🟠 DOMÍNIO LONGO
    # =========================
    if len(dominio) > 30:
        riscos.append("Domínio muito longo")
        score += 10

    # =========================
    # 🔴 SUBDOMÍNIO FALSO
    # =========================
    partes = dominio.split(".")
    if len(partes) > 3:
        for marca in MARCAS:
            if marca in dominio and not dominio.startswith(marca):
                riscos.append(f"Imitação de {marca}")
                score += 35

    # =========================
    # 🔬 ENTROPIA
    # =========================
    try:
        entropia = calcular_entropia(dominio)
        if entropia > 4.2:
            riscos.append("Domínio aleatório (alta entropia)")
            score += 30
    except:
        pass

    # =========================
    # 🧪 PADRÕES SUSPEITOS
    # =========================
    if dominio.count("-") >= 3:
        riscos.append("Muitos hífens no domínio")
        score += 10

    if re.search(r"(123|999|000)", dominio):
        riscos.append("Padrão numérico suspeito")
        score += 8

    # =========================
    # 🧠 CONSENSO (MÚLTIPLOS SINAIS)
    # =========================
    sinais = len(riscos)

    if sinais >= 3:
        score *= 1.2  # aumenta risco se muitos sinais

    # =========================
    # 🎯 NORMALIZAÇÃO
    # =========================
    score = int(min(score, 100))

    # =========================
    # 🧠 AUTO APRENDIZADO
    # =========================
    if dominio not in db:
        db[dominio] = score
    else:
        db[dominio] = int((db[dominio] + score) / 2)

    salvar_db(db)

    return {
        "score": score,
        "riscos": list(set(riscos)) if riscos else []
    }
