import json
import re

def carregar_json(nome_arquivo):
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def normalizar_nome(nome):
    return re.sub(r"\s+", " ", nome.strip().lower())

def verificar_disponibilidade():
    usuarios = carregar_json("usuarios_extraidos.json")
    bloqueios = carregar_json("bloqueios_extraidos.json")

    bloqueios_por_usuario = {}

    for b in bloqueios:
        descricao = b.get("descricao", "")
        desc_normalizado = normalizar_nome(descricao)
        for user in usuarios:
            nome_user = normalizar_nome(user["name"])
            if nome_user in desc_normalizado:
                datas = re.findall(r"(\d{2}/\d{2}/\d{4})", descricao)
                bloqueios_por_usuario.setdefault(user["name"], []).append({
                    "datas": datas,
                    "descricao": descricao.strip()
                })

    print("📋 Relatório de disponibilidade (ordenado):\n")

    # 🔤 Ordena os usuários pelo nome
    usuarios_ordenados = sorted(usuarios, key=lambda u: u["name"].lower())

    for user in usuarios_ordenados:
        nome = user["name"]
        if nome in bloqueios_por_usuario:
            entradas = bloqueios_por_usuario[nome]
            datas_flat = [data for b in entradas for data in b["datas"]]
            datas_str = ", ".join(sorted(set(datas_flat)))
            print(f"⛔ {nome} — bloqueado em {datas_str if datas_str else 'data não especificada'}")
        else:
            print(f"✅ {nome} — disponível")

if __name__ == "__main__":
    verificar_disponibilidade()
