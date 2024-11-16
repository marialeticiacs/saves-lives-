from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional
import os
from fastapi.responses import HTMLResponse

# Modelo para o alerta
class Alerta(BaseModel):
    nome: str
    tipo: str
    condicao: str
    estado: str  
    ativo: bool

# Configuração do MongoDB Atlas
MONGODB_URI = f"mongodb+srv://luyza2129:aUERSWI4GO8mtMsl@pifinal.i7fuk.mongodb.net/?retryWrites=true&w=majority&appName=PIFINAL"
client = MongoClient(MONGODB_URI)
db = client['saves_lives_db']  
alertas_collection = db['alertas'] 

client = MongoClient(
    MONGODB_URI,
    tls=True,  # Ativa o TLS/SSL
    tlsAllowInvalidCertificates=False  # Certifica-se de que certificados inválidos são rejeitados
)


router = APIRouter()

def alerta_to_dict(alerta):
    alerta["_id"] = str(alerta["_id"])
    return alerta


# Rota para exibir a página de criação de alertas
@router.get("/criar", response_class=HTMLResponse)
async def alertas_page():
    file_path = "C:/MariaLetícia/saves-lives-plus/saves-lives/frontend/css/js/alertas.html" #não esquecer de mudar para o seu caminho
    with open(file_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Rota para criar um novo alerta
@router.post("/", response_model=dict)
async def criar_alerta(alerta: Alerta):
    try:
        alerta_id = alertas_collection.insert_one(alerta.dict()).inserted_id
        return {"mensagem": "Alerta criado com sucesso!", "id": str(alerta_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar o alerta: " + str(e))

# Rota para listar todos os alertas
@router.get("/lista", response_model=dict)
async def listar_alertas():
    try:
        alertas = [alerta_to_dict(alerta) for alerta in alertas_collection.find({})]
        return {"alertas": alertas}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao listar alertas: " + str(e))

# Rota para atualizar o status de um alerta
@router.put("/{alerta_id}/status", response_model=dict)
async def atualizar_status_alerta(alerta_id: str, ativo: bool):
    try:
        resultado = alertas_collection.update_one({"_id": ObjectId(alerta_id)}, {"$set": {"ativo": ativo}})
        if resultado.modified_count == 1:
            return {"mensagem": "Status do alerta atualizado com sucesso"}
        else:
            return {"mensagem": "Nenhuma atualização foi feita"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao atualizar o status do alerta: " + str(e))

# Rota para obter detalhes de um alerta específico
@router.get("/{alerta_id}", response_model=dict)
async def obter_alerta(alerta_id: str):
    try:
        alerta = alertas_collection.find_one({"_id": ObjectId(alerta_id)})
        if alerta:
            return alerta_to_dict(alerta)
        else:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao obter o alerta: " + str(e))

# Rota para deletar um alerta
@router.delete("/{alerta_id}", response_model=dict)
async def deletar_alerta(alerta_id: str):
    try:
        resultado = alertas_collection.delete_one({"_id": ObjectId(alerta_id)})
        if resultado.deleted_count == 1:
            return {"mensagem": "Alerta deletado com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao deletar o alerta: " + str(e))
