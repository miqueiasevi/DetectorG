import re

def deep_scan(html, url):
    score = 0
    detections = []

    html_lower = html.lower()

    # =========================
    # 🔎 PHISHING DETECTION
    # =========================
    if "<form" in html_lower and "password" in html_lower:
        score += 30
        detections.append("Possível formulário de phishing detectado")

    if "verify your account" in html_lower or "update your account" in html_lower:
        score += 20
        detections.append("Texto suspeito típico de phishing")

    # =========================
    # 🧠 JAVASCRIPT OFUSCADO
    # =========================
    suspicious_js_patterns = [
        "eval(",
        "atob(",
        "unescape(",
        "string.fromcharcode",
        "document.write(",
        "window.location",
    ]

    for pattern in suspicious_js_patterns:
        if pattern in html_lower:
            score += 15
            detections.append(f"Uso suspeito de JavaScript: {pattern}")

    # Código base64 muito grande
    base64_matches = re.findall(r"[A-Za-z0-9+/=]{200,}", html)
    if len(base64_matches) > 0:
        score += 25
        detections.append("Possível código ofuscado em Base64")

    # =========================
    # 🚨 DRIVE-BY DOWNLOAD
    # =========================
    if "download" in html_lower and "iframe" in html_lower:
        score += 25
        detections.append("Possível drive-by download detectado")

    # =========================
    # 🔁 REDIRECIONAMENTO OCULTO
    # =========================
    if "meta http-equiv=\"refresh\"" in html_lower:
        score += 20
        detections.append("Redirecionamento automático via META refresh")

    if "window.location" in html_lower:
        score += 15
        detections.append("Redirecionamento automático via JavaScript")

    # =========================
    # 🛡️ XSS BÁSICO
    # =========================
    if "<script>" in html_lower and "innerhtml" in html_lower:
        score += 20
        detections.append("Possível vulnerabilidade XSS detectada")

    # =========================
    # 🎯 CLASSIFICAÇÃO FINAL
    # =========================
    if score >= 70:
        risk = "PERIGOSO"
    elif score >= 40:
        risk = "SUSPEITO"
    else:
        risk = "SEGURO"

    return {
        "score": score,
        "risk": risk,
        "detections": detections
      }
