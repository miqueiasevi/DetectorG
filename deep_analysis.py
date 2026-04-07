import requests
import re
from urllib.parse import urlparse
from threat_intel import check_threat_intel  # 🔥 INTEGRAÇÃO

def deep_scan(url):
    riscos = []
    score = 0

    # 🔥 Corrige URL sem http
    if not url.startswith("http"):
        url = "http://" + url

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            timeout=5,
            allow_redirects=True,
            headers=headers
        )

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
    # 🔥 THREAT INTEL (NOVO)
    # =========================
    intel = check_threat_intel(url)
    score += intel["score"]
    riscos.extend(intel["riscos"])

    # =========================
    # 🔴 REDIRECIONAMENTO OCULTO
    # =========================
    if response.url != url:
        riscos.append("Redirecionamento oculto")
        score += 25

    # =========================
    # 🔴 PHISHING AVANÇADO
    # =========================
    if any(p in url for p in ["login", "verify", "secure", "account"]):
        riscos.append("Palavras típicas de phishing")
        score += 15

    if re.search(r"g00gle|faceb00k|paypa1|instagrarn", dominio):
        riscos.append("Domínio falsificado (typosquatting)")
        score += 40

    marcas = ["google", "facebook", "paypal", "instagram", "bank"]
    for m in marcas:
        if m in dominio and m not in dominio.split(".")[0]:
            riscos.append(f"Possível phishing imitando {m}")
            score += 35

    if "paypal" in html and "paypal.com" not in dominio:
        riscos.append("Possível phishing de marca (PayPal)")
        score += 50

    if "<input" in html and "password" in html:
        riscos.append("Página com campo de senha")
        score += 30

    # =========================
    # 🔴 MALWARE / SCRIPTS
    # =========================
    if any(url.endswith(ext) for ext in [".exe", ".apk", ".zip", ".rar"]):
        riscos.append("Download potencialmente malicioso")
        score += 60

    if "eval(" in html and "script" in html:
        riscos.append("Execução dinâmica perigosa")
        score += 40

    if "atob(" in html:
        riscos.append("Código ofuscado detectado")
        score += 40

    if "document.write" in html:
        riscos.append("Script dinâmico suspeito")
        score += 20

    if "download" in html and "<a" in html:
        riscos.append("Download oculto detectado")
        score += 25

    if "keydown" in html or "keyup" in html:
        riscos.append("Captura de teclado suspeita")
        score += 35

    # =========================
    # 🟠 XSS
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
    # 🟠 CSRF
    # =========================
    if "<form" in html and "action=" in html:
        riscos.append("Formulário enviando dados")
        score += 25

    if "<form" in html and "method=\"post\"" in html and "csrf" not in html:
        riscos.append("Formulário sem proteção CSRF")
        score += 25

    # =========================
    # 🟠 URL OFUSCADA
    # =========================
    if "@" in url:
        riscos.append("URL ofuscada com @")
        score += 30

    if any(x in url for x in ["%20", "%3c", "%3e"]):
        riscos.append("URL codificada/ofuscada")
        score += 20

    # =========================
    # 🟠 URL ENCURTADA
    # =========================
    encurtadores = ["bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly"]

    if any(short in dominio for short in encurtadores):
        riscos.append("Link encurtado (destino escondido)")
        score += 30

    # =========================
    # 🟠 REDIRECTS
    # =========================
    if len(history) > 2:
        riscos.append("Muitos redirecionamentos")
        score += 30

    if "window.location" in html:
        riscos.append("Redirecionamento via script")
        score += 20

    # =========================
    # 🟠 DOMÍNIO SUSPEITO
    # =========================
    if dominio.count(".") > 3:
        riscos.append("Muitos subdomínios")
        score += 20

    if re.match(r"\d+\.\d+\.\d+\.\d+", dominio):
        riscos.append("Uso de IP direto (pharming)")
        score += 40

    # =========================
    # 🟠 IFRAME
    # =========================
    if "<iframe" in html:
        riscos.append("Uso de iframe suspeito")
        score += 20

    # =========================
    # 🟠 HTTPS
    # =========================
    if not url.startswith("https"):
        riscos.append("Sem HTTPS (inseguro)")
        score += 10

    # =========================
    # 🟠 CRYPTO SCAM
    # =========================
    if "bitcoin" in html or "wallet" in html:
        riscos.append("Possível golpe com criptomoeda")
        score += 20

    # =========================
    # 🎯 SCORE FINAL
    # =========================
    score = min(score, 100)

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
