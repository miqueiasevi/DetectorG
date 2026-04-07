from crawler import crawler
from deep_analysis import deep_scan

def iniciar():
    url = input("Digite a URL inicial: ").strip()

    print("\n🔍 Iniciando varredura...\n")

    # 1️⃣ Crawler coleta várias URLs
    urls_encontradas = crawler(url, profundidade=2)

    print(f"\n🌐 {len(urls_encontradas)} URLs encontradas\n")

    # 2️⃣ Analisa cada URL com seu motor inteligente
    for link in urls_encontradas:
        print(f"\n🔎 Analisando: {link}")

        resultado = deep_scan(link)

        print(f"Score: {resultado['score']}")
        print(f"Nível: {resultado['nivel']}")
        print(f"Confiança: {resultado.get('confianca', 'N/A')}")
        print("Riscos:")

        for r in resultado["riscos"]:
            print(f" - {r}")

        print("-" * 40)

if __name__ == "__main__":
    iniciar()
