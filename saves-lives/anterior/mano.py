import json
import folium
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, WeatherData
from datetime import datetime

app = FastAPI()

# Carrega o arquivo GeoJSON com os limites dos estados brasileiros
with open("brazil-states.geojson", "r", encoding="utf-8") as f:
    brazil_states_geojson = json.load(f)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para obter dados climáticos por estado
def get_data_for_state(db, state_name):
    result = db.query(
        func.avg(WeatherData.temperatura).label("media_temperatura"),
        func.avg(WeatherData.umidade).label("media_umidade"),
        func.avg(WeatherData.vento).label("media_vento")
    ).filter(WeatherData.local == state_name).first()

    if result and any([result.media_temperatura, result.media_umidade, result.media_vento]):
        return {
            "media_temperatura": round(result.media_temperatura, 1) if result.media_temperatura else "N/A",
            "media_umidade": round(result.media_umidade, 1) if result.media_umidade else "N/A",
            "media_vento": round(result.media_vento, 1) if result.media_vento else "N/A",
        }
    return None

# Função para adicionar popups com dados climáticos
def popup_html(state_name, db):
    data = get_data_for_state(db, state_name)
    if data:
        return f"""
            <b>Estado:</b> {state_name}<br>
            <b>Temperatura Média:</b> {data['media_temperatura']} °C<br>
            <b>Umidade Média:</b> {data['media_umidade']} %<br>
            <b>Vento Médio:</b> {data['media_vento']} km/h
        """
    else:
        print(f"Dados climáticos não encontrados para o estado: {state_name}")
        return f"<b>Estado:</b> {state_name}<br>Dados climáticos não disponíveis."


@app.get("/mapa/estados/", response_class=HTMLResponse)
async def mapa_estados():
    # Cria o mapa centrado no Brasil
    mapa = folium.Map(location=[-14.235, -51.9253], zoom_start=4)

    # Adiciona a camada GeoJSON ao mapa
    folium.GeoJson(
        brazil_states_geojson,
        name="Estados Brasileiros",
        style_function=lambda feature: {
            "fillColor": "#C0C0C0",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
        highlight_function=lambda x: {"weight": 3, "color": "blue", "fillOpacity": 0.7},
        tooltip=folium.features.GeoJsonTooltip(
            fields=["name"],
            aliases=["Estado: "],
            localize=True
        )
    ).add_to(mapa)

    # Salva o mapa em HTML temporariamente
    mapa_html = "mapa_estados.html"
    mapa.save(mapa_html)

    # Carrega o HTML e injeta o link para o arquivo JavaScript e a div lateral
    with open(mapa_html, "r") as f:
        html_content = f.read()

    # Insere o link para o JavaScript e a estrutura da div lateral
    html_content += """
    <style>
        #info-container {
            position: fixed;
            top: 10px;
            right: 10px;
            width: 250px;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            background-color: white;
            font-family: Arial, sans-serif;
            display: none;
        }
        #info-container h3 {
            margin-top: 0;
            color: #333;
        }
        #info-container p {
            margin: 5px 0;
        }
    </style>

    <div id="info-container">
        <h3>Informações do Estado</h3>
        <p id="estado-nome"></p>
        <p id="estado-temperatura"></p>
        <p id="estado-clima"></p>
        <p id="estado-umidade"></p>
        <p id="estado-vento"></p>
    </div>

    <script src="/static/mapa_estados.js"></script>
    """

    return HTMLResponse(content=html_content)
