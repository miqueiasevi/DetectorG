# deep_analysis.py
import re
from urllib.parse import urlparse

def deep_scan(link):
    """
    Análise avançada PRO
    Retorna: {nivel: str, riscos: [str]}
    """
    url = link.lower()
    riscos = []
    score = 0

    # ---------- PHISHING AVANÇADO ----------
    phishing_keywords = [
        "login", "verify", "secure", "account", "update", "premio", "conta",
        "bank", "paypal", "ebay", "google", "apple"
    ]
    # Detecta palavras suspeitas no domínio
    parsed = urlparse(url)
    dominio = parsed.netloc
    for word in phishing_keywords:
        if word in url:
            riscos.append("Phishing")
            score += 30

    # Domínios estranhos / TLD suspeitos
    suspeitos_tld = [".xyz", ".top", ".tk", ".info", ".club", ".online"]
    for tld in suspeitos_tld:
        if dominio.endswith(tld):
            riscos.append("Phishing TLD suspeito")
            score += 20

    # ---------- XSS ----------
    xss_patterns = [
        r"<script.*?>", r"javascript:", r"onerror=", r"onload=",
        r"document\.cookie", r"%3cscript", r"alert\(", r"eval\("
    ]
    for pattern in xss_patterns:
        if re.search(pattern, url):
            riscos.append("XSS")
            score += 40

    # ---------- CSRF ----------
    if "csrf" in url or "token=" in url:
        riscos.append("CSRF")
        score += 20

    # ---------- DRIVE-BY DOWNLOAD ----------
    downloads = [".exe", ".apk", ".msi", ".zip", ".rar", ".bat", ".scr"]
    for ext in downloads:
        if ext in url:
            riscos.append("Drive-by Download")
            score += 50

    # ---------- HEURÍSTICA AVANÇADA ----------
    # URL encurtada
    encurtadas = ["bit.ly", "tinyurl", "goo.gl", "ow.ly", "t.co"]
    for short in encurtadas:
        if short in url:
            riscos.append("URL encurtada suspeita")
            score += 20

    # IP direto no link
    if re.match(r"http[s]?://\d{1,3}(\.\d{1,3}){3}", url):
        riscos.append("IP direto no link")
        score += 20

    # Subdomínios estranhos (muitos níveis)
    subdomens = dominio.split(".")
    if len(subdomens) > 3:
        riscos.append("Subdomínio estranho")
        score += 15

    # ---------- NÍVEL DE RISCO ----------
    nivel = "🟢 Baixo"
    if score >= 30 and score < 70:
        nivel = "🟡 Médio"
    elif score >= 70:
        nivel = "🔴 Alto"

    # Remove duplicados
    riscos = list(set(riscos))

    return {"nivel": nivel, "riscos": riscos}
