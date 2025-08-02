import requests
import json

def search_user():
    print("📡 Buscando usuários...")

    url = "https://www.timbragemplan.com.br/MemberTeam/GetAllMembers"

    # Carrega os cookies salvos
    with open("timbragem_cookies.json", "r") as f:
        cookies_dict = json.load(f)

    cookies = {cookie["name"]: cookie["value"] for cookie in cookies_dict}

    # Faz a requisição
    resp = requests.get(url, cookies=cookies)
    print("📡 Status HTTP:", resp.status_code)

    try:
        data = resp.json()
    except Exception as e:
        print("❌ Erro ao processar resposta:", e)
        print("📄 Conteúdo recebido (início):\n", resp.text[:500])
        return

    # Lista de palavras-chave que indicam posições que devem ser ignoradas
    palavras_excluidas = ["igreja da criança", "pa", "operador de audio"]

    usuarios_extraidos = []
    for user in data:
        posicoes_filtradas = []
        for pos in user.get("organizationTeamPositions", []):
            nome_time = pos.get("organizationTeamName", "").lower()
            nome_posicao = pos.get("name", "").lower()

            if any(p in nome_time for p in palavras_excluidas) or any(p in nome_posicao for p in palavras_excluidas):
                continue

            posicoes_filtradas.append({
                "id": pos.get("id"),
                "name": pos.get("name"),
                "organizationTeamName": pos.get("organizationTeamName"),
                "organizationTeamId": pos.get("organizationTeamId")
            })

        if not posicoes_filtradas:
            continue

        usuario = {
            "id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
            "organizationTeamPositions": posicoes_filtradas
        }

        usuarios_extraidos.append(usuario)

    with open("usuarios_extraidos.json", "w", encoding="utf-8") as f:
        json.dump(usuarios_extraidos, f, indent=2, ensure_ascii=False)

    print(f"✅ Total de usuários salvos: {len(usuarios_extraidos)}")
    print("📁 Arquivo salvo como: usuarios_extraidos.json")
