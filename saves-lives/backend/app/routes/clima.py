from fastapi import APIRouter, Query, HTTPException
import requests
import os

router = APIRouter()

# Chave e URL da API de clima
OWM_API_KEY = "7448e6299383b00ae5d0ce6dd4df2627"
OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"
PREVISAO_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

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
        alerta = None
        if data["main"]["temp"] > 35:
            alerta = "Alerta de Calor Extremo"
        elif data["main"]["temp"] < 5:
            alerta = "Alerta de Frio Intenso"
        if "rain" in data and data["rain"].get("1h", 0) > 10:
            alerta = "Alerta de Chuva Intensa"
        if "wind" in data and data["wind"]["speed"] > 50:
            alerta = "Alerta de Vento Forte"

        return {
            "local": data["name"],
            "temperatura": data["main"]["temp"],
            "clima": data["weather"][0]["description"],
            "umidade": data["main"]["humidity"],
            "vento": data["wind"]["speed"],
            "alerta": alerta or "Nenhum alerta ativo"
        }
    else:
        return {"erro": "Não foi possível obter os dados climáticos"}

@router.get("/estado/previsao")
async def previsao_estado(estado: str = Query(...)):
    params = {
        "q": estado + ",BR",
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "pt"
    }
    response = requests.get(PREVISAO_API_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        previsoes = [
            {
                "data_hora": previsao["dt_txt"],
                "temperatura": previsao["main"]["temp"],
                "clima": previsao["weather"][0]["description"],
                "umidade": previsao["main"]["humidity"],
                "vento": previsao["wind"]["speed"]
            }
            for previsao in data["list"]
        ]
        return {"previsoes": previsoes[:40]}
    else:
        return {"erro": "Não foi possível obter os dados de previsão"}
