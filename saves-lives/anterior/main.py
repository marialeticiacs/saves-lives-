from fastapi import FastAPI, Query
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
import os


app = FastAPI()

# Substitua pela sua chave de API do OpenWeatherMap
OWM_API_KEY = "7448e6299383b00ae5d0ce6dd4df2627"
OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"
app.mount("/static", StaticFiles(directory="static"), name="static")

alertas_configurados = []
ALERTAS_FILE = "alertas.json"


# Rota para servir o index.html
@app.get("/", response_class=HTMLResponse)
async def root():
    # Ajuste o caminho aqui, se o arquivo estiver em 'templates/index.html'
    file_path = os.path.join("templates", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Rota para servir o alertas.html
@app.get("/alertas", response_class=HTMLResponse)
async def alertas_page():
    with open("templates/alertas.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/clima/estado")
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
        # Cria alertas básicos com base nas condições climáticas
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

@app.get("/clima/estado/previsao")
async def previsao_estado(estado: str = Query(...)):
    previsao_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": estado + ",BR",
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "pt"
    }
    response = requests.get(previsao_url, params=params)
    data = response.json()

    if response.status_code == 200:
        previsoes = []
        for previsao in data["list"]:
            previsoes.append({
                "data_hora": previsao["dt_txt"],
                "temperatura": previsao["main"]["temp"],
                "clima": previsao["weather"][0]["description"],
                "umidade": previsao["main"]["humidity"],
                "vento": previsao["wind"]["speed"]
            })

        return {"previsoes": previsoes[:40]}  # Retorna as 40 primeiras previsões como exemplo
    else:
        return {"erro": "Não foi possível obter os dados de previsão"}



# Estrutura de dados para um alerta
class Alerta(BaseModel):
    tipo: str  # Tipo de alerta, ex: "Temperatura muito baixa"
    condicao: str  # Condição, ex: "abaixo de 10°C"
    ativo: bool  # Se o alerta está ativo ou não

# Rota para listar alertas configurados
@app.get("/alertas", response_model=List[Alerta])
async def listar_alertas():
    return alertas_configurados

# Rota para adicionar ou atualizar um alerta
@app.post("/alertas")
async def criar_alerta(alerta: Alerta):
    for i, a in enumerate(alertas_configurados):
        if a.tipo == alerta.tipo:
            alertas_configurados[i] = alerta  # Atualiza o alerta se ele já existir
            return {"mensagem": "Alerta atualizado com sucesso"}
    alertas_configurados.append(alerta)
    return {"mensagem": "Alerta criado com sucesso"}



# Suponha que você tenha uma lista de alertas salva
alertas_salvos = [
    {"tipo": "Temperatura alta", "condicao": "acima de 30°C", "ativo": True},
    {"tipo": "Temperatura baixa", "condicao": "abaixo de 15°C", "ativo": True},
    # Adicione mais alertas conforme necessário
]

@app.get("/alertas/lista", response_class=HTMLResponse)
async def lista_alertas(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lista de Alertas</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f2f5; }
            .container { max-width: 600px; margin: 20px auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); }
            .alert-item { padding: 10px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; }
            .alert-item:last-child { border-bottom: none; }
            .alert-title { font-weight: bold; color: #4CAF50; }
            .alert-condition, .alert-status { color: #555; }
            .button-group { display: flex; gap: 5px; }
            .button { padding: 5px 10px; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
            .edit-btn { background-color: #007BFF; }
            .delete-btn { background-color: #FF4B4B; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Lista de Alertas</h1>
            <div id="alert-list">
    """
    for i, alerta in enumerate(alertas_salvos):
        status = "Ativo" if alerta["ativo"] else "Inativo"
        html_content += f"""
                <div class="alert-item">
                    <div>
                        <div class="alert-title">Tipo: {alerta["tipo"]}</div>
                        <div class="alert-condition">Condição: {alerta["condicao"]}</div>
                        <div class="alert-status">Status: {status}</div>
                    </div>
                    <div class="button-group">
                        <button class="button edit-btn" onclick="editarAlerta({i})">Editar</button>
                        <button class="button delete-btn" onclick="deletarAlerta({i})">Excluir</button>
                    </div>
                </div>
        """
    html_content += """
            </div>
            <button onclick="window.location.href='/alertas'">Voltar para Configurar Alertas</button>
        </div>
        <script>
            function editarAlerta(id) {
                const novoTipo = prompt("Digite o novo tipo de alerta:");
                const novaCondicao = prompt("Digite a nova condição (ex: acima de 30°C):");
                const novoStatus = confirm("Marque OK para Ativo e Cancelar para Inativo");
                
                if (novoTipo && novaCondicao) {
                    fetch(`/alertas/${id}`, {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            tipo: novoTipo,
                            condicao: novaCondicao,
                            ativo: novoStatus
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.mensagem) {
                            alert(data.mensagem);
                            location.reload();  // Atualiza a página
                        } else {
                            alert("Erro ao atualizar o alerta.");
                        }
                    })
                    .catch(error => console.error("Erro ao atualizar alerta:", error));
                }
            }

            function deletarAlerta(id) {
                if (confirm("Tem certeza que deseja excluir este alerta?")) {
                    fetch(`/alertas/${id}`, {
                        method: "DELETE"
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.mensagem) {
                            alert(data.mensagem);
                            location.reload();  // Atualiza a página
                        } else {
                            alert("Erro ao excluir o alerta.");
                        }
                    })
                    .catch(error => console.error("Erro ao excluir alerta:", error));
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)



# Carregar alertas do arquivo JSON, se existir
def carregar_alertas():
    if os.path.exists(ALERTAS_FILE):
        with open(ALERTAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Salvar alertas no arquivo JSON
def salvar_alertas(alertas):
    with open(ALERTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(alertas, f, ensure_ascii=False, indent=4)

alertas_configurados = carregar_alertas()

# Estrutura de dados para um alerta
class Alerta(BaseModel):
    tipo: str  # Tipo de alerta, ex: "Temperatura muito baixa"
    condicao: str  # Condição, ex: "abaixo de 10°C"
    ativo: bool  # Se o alerta está ativo ou não

# Rota para listar alertas configurados
@app.get("/alertas", response_model=List[Alerta])
async def listar_alertas():
    return alertas_configurados

# Rota para adicionar um alerta
@app.post("/alertas")
async def criar_alerta(alerta: Alerta):
    alertas_configurados.append(alerta.dict())
    salvar_alertas(alertas_configurados)
    return {"mensagem": "Alerta criado com sucesso"}
from fastapi import FastAPI, HTTPException

# Atualizar alerta existente
@app.put("/alertas/{alerta_id}")
async def atualizar_alerta(alerta_id: int, alerta_atualizado: Alerta):
    if alerta_id < 0 or alerta_id >= len(alertas_configurados):
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    alertas_configurados[alerta_id] = alerta_atualizado
    salvar_alertas()  # Salva as mudanças
    return {"mensagem": "Alerta atualizado com sucesso"}

# Deletar alerta
@app.delete("/alertas/{alerta_id}")
async def deletar_alerta(alerta_id: int):
    if alerta_id < 0 or alerta_id >= len(alertas_configurados):
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    alertas_configurados.pop(alerta_id)
    salvar_alertas()  # Salva as mudanças
    return {"mensagem": "Alerta deletado com sucesso"}



# Carregar o arquivo de rotas
def carregar_rotas():
    with open("rotas.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/rotas", response_class=JSONResponse)
async def obter_rotas():
    try:
        rotas = carregar_rotas()
        return rotas
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao carregar as rotas")
