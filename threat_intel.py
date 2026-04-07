import re
import math
from urllib.parse import urlparse

# =========================
# BASE LOCAL (EXPANDÍVEL)
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

DOMINIOS_SUSPEITOS = [
    ".xyz", ".tk", ".top", ".gq", ".ml"
]

ENCURTADORES = [
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly"
]

MARCAS = ["google", "facebook", "paypal", "instagram", "bank"]

# =========================
# 🔬 ENTROPIA (detecção de domínio estranho)
# =========================
def calcular_entropia(texto):
    prob = [float(texto.count(c)) / len(texto) for c in set(texto)]
    return -sum([p * math.log2(p) for p in prob])

# =========================
# 🚀 FUNÇÃO PRINCIPAL
# =========================
def check_threat_intel(url):
    riscos = []
    score = 0

    dominio = urlparse(url).netloc.lower()

    # =========================
    # 🔴 BLACKLIST
    # =========================
    if dominio in BLACKLIST_DOMINIOS:
        riscos.append("Domínio em blacklist")
        score += 90

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
        score += 25

    # =========================
    # 🟠 URL ENCURTADA
    # =========================
    if any(short in dominio for short in ENCURTADORES):
        riscos.append("URL encurtada")
        score += 30

    # =========================
    # 🟠 DOMÍNIO LONGO
    # =========================
    if len(dominio) > 30:
        riscos.append("Domínio muito longo")
        score += 15

    # =========================
    # 🔴 SUBDOMÍNIO FALSO
    # Ex: google.login.seguro.xyz
    # =========================
    partes = dominio.split(".")
    if len(partes) > 3:
        for marca in MARCAS:
            if marca in dominio and not dominio.startswith(marca):
                riscos.append("Subdomínio imitando marca")
                score += 40

    # =========================
    # 🔬 ENTROPIA (detecção malware)
    # =========================
    try:
        entropia = calcular_entropia(dominio)
        if entropia > 4:
            riscos.append("Domínio aleatório (alta entropia)")
            score += 35
    except:
        pass

    # =========================
    # 🧪 PADRÕES SUSPEITOS
    # =========================
    if dominio.count("-") >= 3:
        riscos.append("Muitos hífens no domínio")
        score += 15

    if any(num in dominio for num in ["123", "999", "000"]):
        riscos.append("Números suspeitos no domínio")
        score += 10

    # =========================
    # 🎯 NORMALIZAÇÃO
    # =========================
    score = min(score, 100)

    return {
        "score": score,
        "riscos": riscos
    }
