from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

# Caminho para o arquivo de rotas
ROTAS_FILE = "C:/Users/luyza/saves-lives/saves-lives/backend/app/data/rotas.json"

# Função para carregar as rotas do arquivo JSON
def carregar_rotas():
    if os.path.exists(ROTAS_FILE):
        with open(ROTAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"rotas": []}

@router.get("/", response_model=dict)
async def obter_rotas():
    try:
        rotas = carregar_rotas()
        return rotas
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao carregar as rotas")
