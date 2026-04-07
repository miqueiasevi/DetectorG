import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from deep_analysis import deep_scan
from collector import registrar_scan

visitados = set()

def extrair_links(url, html):
    links = set()
    soup = BeautifulSoup(html, "html.parser")

    for a in soup.find_all("a", href=True):
        link = urljoin(url, a["href"])

        # Apenas http(s)
        if link.startswith("http"):
            links.add(link)

    return links


def crawler(url, profundidade=2):
    if profundidade == 0 or url in visitados:
        return

    visitados.add(url)

    try:
        print(f"🔎 Analisando: {url}")

        response = requests.get(url, timeout=5)
        html = response.text

        # 🔥 ANALISA O SITE
        resultado = deep_scan(url)

        # 💾 SALVA NO BANCO
        registrar_scan(url, resultado)

        # 🕷️ PEGA LINKS
        links = extrair_links(url, html)

        # 🔁 CRAWL RECURSIVO
        for link in links:
            crawler(link, profundidade - 1)

    except:
        print(f"⚠️ Erro ao acessar {url}")
