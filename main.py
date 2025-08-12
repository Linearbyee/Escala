from fastapi import FastAPI
from login import fazer_login
from puxar_eventos import buscar_eventos
from read_block import buscar_bloqueios
from busca_usuarios import search_user
from search_user_block import verificar_disponibilidade
import json
import os

app = FastAPI()

EMAIL = "garcia.phsp@hotmail.com"
SENHA = "Phsp38082902"

def carregar_json(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        return {"erro": f"{caminho_arquivo} não encontrado."}
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        return json.load(f)
    
@app.get("/puxarEventos")
def api_puxar_eventos():
    if fazer_login(EMAIL, SENHA, headless=True):
        buscar_eventos()
        return carregar_json("eventos_extraidos.json")
    return {"erro": "Falha no login"}

@app.get("/bloqueios")
def api_puxar_bloqueios():
    if fazer_login(EMAIL, SENHA, headless=True):
        buscar_bloqueios()
        return carregar_json("bloqueios_extraidos.json")
    return {"erro": "Falha no login"}

@app.get("/usuarios")
def api_puxar_usuarios():
    if fazer_login(EMAIL, SENHA, headless=True):
        search_user()
        return carregar_json("usuarios_extraidos.json")
    return {"erro": "Falha no login"}

@app.get("/verificarDisponibilidade")
def api_verificar_disponibilidade():
    resultado = verificar_disponibilidade()
    return resultado["bloqueado"]