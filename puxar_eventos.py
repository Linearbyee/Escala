import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re
from datetime import datetime

COOKIE_PATH = "timbragem_cookies.json"
URL_EVENTS_PAGE = "https://www.timbragemplan.com.br/events"
OUTPUT_FILE = "eventos_extraidos.json"

MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12
}

def extrair_event_id(container):
    a = container.select_one('a[href*="/events/edit?eventId="]')
    if not a:
        return ""
    href = a.get("href", "")
    try:
        q = parse_qs(urlparse(href).query)
        return q.get("eventId", [""])[0]
    except Exception:
        return ""

def extrair_hora(texto):
    # pega "10:00h" ou "10:00"
    m = re.search(r"(\d{1,2}:\d{2})h?", texto)
    return m.group(1) if m else ""

def parse_data_pt(texto):
    """
    Retorna (YYYY, MM, DD) se conseguir interpretar a data no texto.
    Prioriza dd/mm/aaaa. Se vier "01 setembro" (sem ano), usa o ano atual.
    """
    # 1) dd/mm/aaaa
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", texto)
    if m:
        d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return y, mth, d

    # 2) "01 setembro" (opcionalmente seguido de ano)
    m = re.search(
        r"\b(\d{1,2})\s+(janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)(?:\s+de\s+(\d{4})|\s+(\d{4}))?\b",
        texto, flags=re.IGNORECASE
    )
    if m:
        d = int(m.group(1))
        mes_nome = m.group(2).lower()
        y = None
        # Tenta ano explicitado
        for g in (3, 4):
            if m.group(g):
                y = int(m.group(g))
                break
        # Se não tiver ano, assume ano atual
        if y is None:
            y = datetime.now().year
        mth = MESES_PT.get(mes_nome, None)
        if mth:
            return y, mth, d

    return None

def formatar_data(y_m_d):
    if not y_m_d:
        return ""
    y, m, d = y_m_d
    try:
        return datetime(y, m, d).strftime("%Y-%m-%d")  # ISO
    except ValueError:
        return ""

def buscar_eventos():
    try:
        with open(COOKIE_PATH, "r", encoding="utf-8") as f:
            cookies_raw = json.load(f)
        cookies = {c["name"]: c["value"] for c in cookies_raw}
    except Exception:
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
        raw_texto = (e.get("data-search-value") or "").strip()

        # eventId a partir do <a href="/events/edit?eventId=...">
        event_id = extrair_event_id(e)

        # hora: tenta dentro do próprio container (prioriza) e depois no raw_texto
        horario_el = e.select_one("strong.text-dark")
        hora_txt = extrair_hora(horario_el.text) if horario_el else extrair_hora(raw_texto)

        # data: tenta em elementos existentes; se vazio, cai pro parse do raw_texto
        # (mantemos compatibilidade, mas normalizamos para ISO no final)
        data_el = e.select_one("span.badge-dark")
        data_bruta = (data_el.text.strip() if data_el else "")
        ymd = parse_data_pt(data_bruta) or parse_data_pt(raw_texto)
        data_iso = formatar_data(ymd)

        eventos_extraidos.append({
            "eventId": event_id,
            "descricao": raw_texto,
            "horario": hora_txt,       # ex.: "10:00"
            "data": data_iso           # ex.: "2025-08-17"
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(eventos_extraidos, f, indent=2, ensure_ascii=False)

    print(f"✅ Eventos extraídos e salvos em: {OUTPUT_FILE}")

if __name__ == "__main__":
    buscar_eventos()
    