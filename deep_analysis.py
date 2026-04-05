import requests
import re
from urllib.parse import urlparse

# =========================
# FUNÇÃO PRINCIPAL
# =========================

def deep_scan(url):
    riscos = []
    score = 0

    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        html = response.text.lower()
        history = response.history
    except:
        return {
            "score": 90,
            "nivel": "🔴 Alto",
            "riscos": ["Site inacessível (possível risco)"]
        }

    dominio = urlparse(url).netloc.lower()

    # =========================
    # 🔴 1. PHISHING AVANÇADO
    # =========================
    if any(p in url for p in ["login", "verify", "secure", "account"]):
        riscos.append("Palavras típicas de phishing")
        score += 15

    if re.search(r"g00gle|faceb00k|paypa1|instagrarn", dominio):
        riscos.append("Domínio falsificado (typosquatting)")
        score += 40

    if "<input" in html and "password" in html:
        riscos.append("Página com campo de senha (possível phishing)")
        score += 30

    # =========================
    # 🔴 2. MALWARE / SCRIPTS
    # =========================
    if any(url.endswith(ext) for ext in [".exe", ".apk", ".zip", ".rar"]):
        riscos.append("Download potencialmente malicioso")
        score += 60

    if "eval(" in html or "atob(" in html:
        riscos.append("Código ofuscado detectado")
        score += 40

    if "document.write" in html:
        riscos.append("Script dinâmico suspeito")
        score += 20

    # =========================
    # 🟠 3. XSS (BÁSICO)
    # =========================
    if "<script" in html:
        riscos.append("Uso de script (possível XSS)")
        score += 20

    if "onerror=" in html or "onload=" in html:
        riscos.append("Evento suspeito (XSS)")
        score += 30

    if "javascript:" in html:
        riscos.append("Execução javascript suspeita")
        score += 20

    # =========================
    # 🟠 4. CSRF (BÁSICO)
    # =========================
    if "<form" in html and "method=\"post\"" in html and "csrf" not in html:
        riscos.append("Formulário sem proteção CSRF")
        score += 25

    # =========================
    # 🟠 5. URL OFUSCADA
    # =========================
    if "@" in url:
        riscos.append("URL ofuscada com @")
        score += 30

    if any(x in url for x in ["%20", "%3c", "%3e"]):
        riscos.append("URL codificada/ofuscada")
        score += 20

    # =========================
    # 🟠 6. URL ENCURTADA
    # =========================
    if any(short in dominio for short in ["bit.ly", "tinyurl", "goo.gl"]):
        riscos.append("URL encurtada (destino oculto)")
        score += 30

    # =========================
    # 🟠 7. REDIRECTS
    # =========================
    if len(history) > 2:
        riscos.append("Muitos redirecionamentos")
        score += 30

    if "window.location" in html:
        riscos.append("Redirecionamento via script")
        score += 20

    # =========================
    # 🟠 8. DOMÍNIO SUSPEITO
    # =========================
    if dominio.count(".") > 3:
        riscos.append("Muitos subdomínios")
        score += 20

    if re.match(r"\d+\.\d+\.\d+\.\d+", dominio):
        riscos.append("Uso de IP direto (pharming)")
        score += 40

    # =========================
    # 🟠 9. IFRAME
    # =========================
    if "<iframe" in html:
        riscos.append("Uso de iframe (possível ataque)")
        score += 20

    # =========================
    # 🟠 10. HTTPS
    # =========================
    if not url.startswith("https"):
        riscos.append("Sem HTTPS (inseguro)")
        score += 10

    # =========================
    # 🎯 NORMALIZA SCORE
    # =========================
    score = min(score, 100)

    # =========================
    # 🎯 CLASSIFICAÇÃO FINAL
    # =========================
    if score < 30:
        nivel = "🟢 Baixo"
    elif score < 70:
        nivel = "🟡 Médio"
    else:
        nivel = "🔴 Alto"

    return {
        "score": score,
        "nivel": nivel,
        "riscos": riscos if riscos else ["Nenhum risco detectado"]
        }
