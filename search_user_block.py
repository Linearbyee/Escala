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
                bloqueios_por_usuario.setdefault(user["name"], []).extend(datas)

    resultado = {"disponível": [], "bloqueado": []}

    for user in sorted(usuarios, key=lambda u: u["name"].lower()):
        nome = user["name"]
        if nome in bloqueios_por_usuario:
            datas_unicas = sorted(set(bloqueios_por_usuario[nome]))
            resultado["bloqueado"].append({"nome": nome, "datas": datas_unicas})
        else:
            resultado["disponível"].append({"nome": nome, "datas": []})

    return resultado
