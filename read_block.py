import requests
import json
from bs4 import BeautifulSoup

def buscar_bloqueios():
    print("📡 Buscando bloqueios...")

    url = "https://www.timbragemplan.com.br/MemberTeam/GetNextBlockoutsList"

    # Carrega os cookies salvos
    with open("timbragem_cookies.json", "r") as f:
        cookies_dict = json.load(f)

    cookies = {cookie["name"]: cookie["value"] for cookie in cookies_dict}

    resp = requests.get(url, cookies=cookies)
    print("📡 Status HTTP:", resp.status_code)

    soup = BeautifulSoup(resp.text, 'html.parser')

    bloqueios = []

    items = soup.select(".blockout-item")
    for item in items:
        descricao = item.get_text(separator=" ", strip=True)
        bloqueios.append({"descricao": descricao})

    print(f"🔢 Total de bloqueios encontrados: {len(bloqueios)}")
    with open("bloqueios_extraidos.json", "w", encoding="utf-8") as f:
        json.dump(bloqueios, f, indent=2, ensure_ascii=False)
    print("✅ Bloqueios salvos em bloqueios_extraidos.json")
