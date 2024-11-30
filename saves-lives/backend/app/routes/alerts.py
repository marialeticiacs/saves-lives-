from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import os
from fastapi import Body

DB_PATH = "alertas.db"

class Alerta(BaseModel):
    nome: str
    tipo: str
    condicao: Optional[str] = None
    estado: str
    ativo: bool

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            condicao TEXT,
            estado TEXT NOT NULL,
            ativo BOOLEAN NOT NULL
        )
        """)
        conn.commit()

init_db()

router = APIRouter()

@router.get("/criar", response_class=HTMLResponse)
async def criar_alerta_page():
    try:
        #file_path = "C:/Users/luyza/PI6/saves-lives-plus/saves-lives/frontend/css/js/alertas.html"  #Não esquecer de mudar aqui para o seu caminho
        
        file_path = "C:/MariaLetícia/saves-lives-plus/saves-lives/frontend/css/js/alertas.html" 
        
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar a página: {str(e)}")

@router.post("/", response_model=dict)
async def criar_alerta(alerta: Alerta):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO alertas (nome, tipo, condicao, estado, ativo)
            VALUES (?, ?, ?, ?, ?)
            """, (alerta.nome, alerta.tipo, alerta.condicao, alerta.estado, alerta.ativo))
            conn.commit()
            return {"mensagem": "Alerta criado com sucesso!", "id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar o alerta: {str(e)}")

@router.get("/lista", response_model=dict)
async def listar_alertas():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alertas")
            alertas = [
                {"id": row[0], "nome": row[1], "tipo": row[2], "condicao": row[3], "estado": row[4], "ativo": bool(row[5])}
                for row in cursor.fetchall()
            ]
            return {"alertas": alertas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar alertas: {str(e)}")

@router.get("/{alerta_id}", response_model=dict)
async def obter_alerta(alerta_id: int):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alertas WHERE id = ?", (alerta_id,))
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "nome": row[1], "tipo": row[2], "condicao": row[3], "estado": row[4], "ativo": bool(row[5])}
            else:
                raise HTTPException(status_code=404, detail="Alerta não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter o alerta: {str(e)}")

@router.delete("/{alerta_id}", response_model=dict)
async def deletar_alerta(alerta_id: int):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alertas WHERE id = ?", (alerta_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return {"mensagem": "Alerta deletado com sucesso"}
            else:
                raise HTTPException(status_code=404, detail="Alerta não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar o alerta: {str(e)}")



@router.put("/{alerta_id}/status", response_model=dict)
async def atualizar_status_alerta(alerta_id: int, ativo: bool):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE alertas SET ativo = ? WHERE id = ?", (ativo, alerta_id))
            conn.commit()
            if cursor.rowcount > 0:
                return {"mensagem": "Status do alerta atualizado com sucesso!"}
            else:
                raise HTTPException(status_code=404, detail="Alerta não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar o status do alerta: {str(e)}")
