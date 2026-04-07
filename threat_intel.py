import re
from urllib.parse import urlparse

# =========================
# BASE LOCAL (pode crescer depois)
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

# =========================
# FUNÇÃO PRINCIPAL
# =========================

def check_threat_intel(url):
    riscos = []
    score = 0

    dominio = urlparse(url).netloc.lower()

    # =========================
    # 🔴 BLACKLIST DOMÍNIOS
    # =========================
    if dominio in BLACKLIST_DOMINIOS:
        riscos.append("Domínio em blacklist")
        score += 80

    # =========================
    # 🔴 IP DIRETO
    # =========================
    if re.match(r"\d+\.\d+\.\d+\.\d+", dominio):
        if dominio in BLACKLIST_IPS:
            riscos.append("IP malicioso conhecido")
            score += 90
        else:
            riscos.append("Uso de IP direto (suspeito)")
            score += 40

    # =========================
    # 🟠 TLD SUSPEITO
    # =========================
    if any(dominio.endswith(tld) for tld in DOMINIOS_SUSPEITOS):
        riscos.append("Domínio com TLD suspeito")
        score += 25

    # =========================
    # 🟠 URL ENCURTADA
    # =========================
    if any(short in dominio for short in ENCURTADORES):
        riscos.append("Serviço de URL encurtada")
        score += 30

    # =========================
    # 🟠 DOMÍNIO MUITO LONGO
    # =========================
    if len(dominio) > 30:
        riscos.append("Domínio muito longo (suspeito)")
        score += 15

    return {
        "score": score,
        "riscos": riscos
    }
