import json
import requests
from bs4 import BeautifulSoup

COOKIE_PATH = "timbragem_cookies.json"
URL_EVENTS_PAGE = "https://www.timbragemplan.com.br/events"
OUTPUT_FILE = "eventos_extraidos.json"

def buscar_eventos():
    try:
        with open(COOKIE_PATH, "r") as f:
            cookies_raw = json.load(f)
        cookies = {c["name"]: c["value"] for c in cookies_raw}
    except:
        print("❌ Cookies não encontrados.")
        return

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html"
    }

    print("➡️ Buscando página de eventos...")
    resp = requests.get(URL_EVENTS_PAGE, cookies=cookies, headers=headers)

    if resp.status_code != 200:
        print(f"❌ Erro HTTP: {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, "lxml")
    eventos_html = soup.select("div.event-list-item")

    eventos_extraidos = []

    for e in eventos_html:
        raw_texto = e.get("data-search-value", "").strip()
        horario = e.select_one("strong.text-dark")
        data = e.select_one("span.badge-dark")

        eventos_extraidos.append({
            "descricao": raw_texto,
            "horario": horario.text.strip() if horario else "",
            "data": data.text.strip() if data else ""
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(eventos_extraidos, f, indent=2, ensure_ascii=False)

    print(f"✅ Eventos extraídos e salvos em: {OUTPUT_FILE}")
