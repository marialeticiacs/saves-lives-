from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()
#Mudar para o seu caminho
ROTAS_JSON_FILE = "C:/MariaLetícia/saves-lives-plus/saves-lives/backend/app/data/rotas_equipes.json"


def carregar_rotas_do_json():
    """
    Função para carregar as rotas do arquivo JSON e remover duplicatas.
    """
    if not os.path.exists(ROTAS_JSON_FILE):
        raise HTTPException(status_code=404, detail="Arquivo de rotas não encontrado.")

    try:
        with open(ROTAS_JSON_FILE, "r", encoding="utf-8") as file:
            rotas = json.load(file)
        
        for rota in rotas["rotas"]:
            coordenadas_unicas = []
            coordenadas_vistas = set()
            for coordenada in rota["coordenadas"]:
                coord_tuple = (coordenada["latitude"], coordenada["longitude"])
                if coord_tuple not in coordenadas_vistas:
                    coordenadas_unicas.append(coordenada)
                    coordenadas_vistas.add(coord_tuple)
            rota["coordenadas"] = coordenadas_unicas

        return rotas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar o arquivo de rotas: {str(e)}")


@router.get("/", response_model=dict)
async def obter_rotas():
    """
    Endpoint para retornar as rotas carregadas do arquivo JSON.
    """
    try:
        rotas = carregar_rotas_do_json()
        return rotas
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter as rotas: {str(e)}")
