import requests
import re
from urllib.parse import urlparse
from threat_intel import check_threat_intel

def deep_scan(url):
    riscos = []

    # 🔥 SCORES SEPARADOS (PROFISSIONAL)
    phishing = 0
    malware = 0
    estrutura = 0
    intel_score = 0

    # Corrige URL
    if not url.startswith("http"):
        url = "http://" + url

    try:
        response = requests.get(
            url,
            timeout=6,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        html = response.text.lower()
        history = response.history

    except:
        return {
            "score": 90,
            "nivel": "🔴 Alto",
            "confianca": 40,
            "riscos": ["Site inacessível"]
        }

    dominio = urlparse(url).netloc.lower()

    # =========================
    # ✅ WHITELIST (ANTI FALSO POSITIVO)
    # =========================
    confiaveis = [
        "google.com", "youtube.com", "github.com",
        "microsoft.com", "apple.com", "amazon.com"
    ]

    if any(d in dominio for d in confiaveis):
        return {
            "score": 5,
            "nivel": "🟢 Baixo",
            "confianca": 98,
            "riscos": ["Domínio confiável"]
        }

    # =========================
    # 🌍 THREAT INTEL
    # =========================
    intel = check_threat_intel(url)
    intel_score += intel["score"]
    riscos.extend(intel["riscos"])

    # =========================
    # 🔴 PHISHING
    # =========================
    if any(p in url for p in ["login", "verify", "secure", "account", "update"]):
        phishing += 10
        riscos.append("URL suspeita")

    if re.search(r"g00gle|faceb00k|paypa1|instagrarn", dominio):
        phishing += 40
        riscos.append("Domínio falsificado")

    if "<input" in html and "password" in html:
        phishing += 25
        riscos.append("Captura de senha")

    if "paypal" in html and "paypal.com" not in dominio:
        phishing += 50
        riscos.append("Phishing PayPal")

    if "login" in html and "password" in html and not url.startswith("https"):
        phishing += 30
        riscos.append("Login inseguro")

    # 🔥 NOVO: formulário externo
    if "<form" in html and "action=http" in html:
        phishing += 20
        riscos.append("Formulário enviando para outro domínio")

    # =========================
    # 🔴 MALWARE
    # =========================
    if any(url.endswith(ext) for ext in [".exe", ".apk", ".zip", ".rar"]):
        malware += 60
        riscos.append("Arquivo perigoso")

    if "eval(" in html:
        malware += 30
        riscos.append("Script suspeito")

    if "atob(" in html:
        malware += 25
        riscos.append("Código oculto")

    if "document.write" in html:
        malware += 15
        riscos.append("Script dinâmico")

    if "keydown" in html or "keyup" in html:
        malware += 25
        riscos.append("Captura de teclado")

    # =========================
    # 🟠 ESTRUTURA
    # =========================
    if response.url != url:
        estrutura += 15
        riscos.append("Redirecionamento")

    if len(history) > 2:
        estrutura += 20
        riscos.append("Muitos redirects")

    if "<iframe" in html:
        estrutura += 10
        riscos.append("Iframe")

    if "@" in url:
        estrutura += 20
        riscos.append("URL mascarada")

    if not url.startswith("https"):
        estrutura += 10
        riscos.append("Sem HTTPS")

    if dominio.count("-") >= 3:
        estrutura += 15
        riscos.append("Domínio suspeito")

    if len(dominio) > 30:
        estrutura += 10
        riscos.append("Domínio muito longo")

    if dominio.count(".") > 3:
        estrutura += 10
        riscos.append("Muitos subdomínios")

    if re.match(r"\d+\.\d+\.\d+\.\d+", dominio):
        estrutura += 40
        riscos.append("Uso de IP")

    # 🔥 NOVO: encurtadores
    if any(s in dominio for s in ["bit.ly", "tinyurl", "t.co"]):
        estrutura += 25
        riscos.append("Link encurtado")

    # =========================
    # 🎯 NORMALIZAÇÃO
    # =========================
    phishing = min(phishing, 60)
    malware = min(malware, 70)
    estrutura = min(estrutura, 40)
    intel_score = min(intel_score, 80)

    # =========================
    # 🎯 SCORE FINAL (MELHORADO)
    # =========================
    score = (
        phishing * 0.35 +
        malware * 0.30 +
        estrutura * 0.20 +
        intel_score * 0.15
    )

    score = int(min(score, 100))

    # =========================
    # 🎯 CONFIANÇA (INTELIGENTE)
    # =========================
    sinais = len(set(riscos))

    if sinais == 0:
        confianca = 95
    elif sinais <= 2:
        confianca = 70
    elif sinais <= 5:
        confianca = 80
    else:
        confianca = 90

    # =========================
    # 🎯 NÍVEL FINAL
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
        "confianca": confianca,
        "riscos": list(set(riscos)) if riscos else ["Nenhum risco detectado"]
        }
