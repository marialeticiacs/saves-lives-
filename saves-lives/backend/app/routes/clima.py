from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import requests
import sqlite3 
router = APIRouter()

OWM_API_KEY = "7448e6299383b00ae5d0ce6dd4df2627"
OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"

def buscar_alertas_personalizados(estado: str, data_climatica: dict) -> list:
    conn = sqlite3.connect("C:/MariaLetícia/saves-lives-plus/saves-lives/backend/app/alertas.db")
    cursor = conn.cursor()

    # Busca alertas ativos
    cursor.execute("""
        SELECT nome, tipo, condicao
        FROM alertas
        WHERE (estado = ? OR estado = 'Todos') AND ativo = 1
    """, (estado,))
    alertas = cursor.fetchall()
    conn.close()

    alertas_filtrados = []

    for nome, tipo, condicao in alertas:
        if condicao:
            try:
                condicao = float(condicao.replace("°C", "").strip())
            except ValueError:
                condicao = None

        if tipo == "Temperatura alta" and condicao and float(data_climatica["main"]["temp"]) > condicao:
            alertas_filtrados.append(f"{nome} (Temperatura > {condicao}°C)")
        elif tipo == "Temperatura baixa" and condicao and float(data_climatica["main"]["temp"]) < condicao:
            alertas_filtrados.append(f"{nome} (Temperatura < {condicao}°C)")
        elif tipo == "Chuva intensa" and "rain" in data_climatica and data_climatica["rain"].get("1h", 0) > float(condicao or 10):
            alertas_filtrados.append(f"{nome} (Chuva intensa)")

    return alertas_filtrados

@router.get("/estado")
async def clima_estado(estado: str = Query(...)):
    params = {
        "q": estado + ",BR",
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "pt"
    }
    response = requests.get(OWM_API_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        alertas = buscar_alertas_personalizados(estado, data)

        return {
            "local": data["name"],
            "temperatura": data["main"]["temp"],
            "clima": data["weather"][0]["description"],
            "umidade": data["main"]["humidity"],
            "vento": data["wind"]["speed"],
            "alerta": alertas if alertas else ["Nenhum alerta ativo"]
        }
    else:
        raise HTTPException(status_code=500, detail="Não foi possível obter os dados climáticos")

@router.get("/estado/previsao")
async def previsao_estado(estado: str):
    OWM_API_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": estado + ",BR",
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "pt"
    }
    response = requests.get(OWM_API_URL_FORECAST, params=params)
    if response.status_code == 200:
        data = response.json()
        previsoes = [
            {
                "data_hora": item["dt_txt"],
                "temperatura": item["main"]["temp"],
                "clima": item["weather"][0]["description"]
            }
            for item in data["list"]
        ]
        return {"previsoes": previsoes}
    else:
        return {"erro": "Não foi possível obter a previsão do tempo"}

