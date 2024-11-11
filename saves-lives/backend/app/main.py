from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.routes import clima, alerts, rotas  # Importa as rotas que vamos configurar
import os

app = FastAPI()

# Inclua as rotas
app.include_router(clima.router, prefix="/clima")
app.include_router(alerts.router, prefix="/alertas")
app.include_router(rotas.router, prefix="/rotas")

# Montando o diretório estático para arquivos como brazil-states.geojson
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota para servir o index.html
@app.get("/", response_class=HTMLResponse)
async def root():
    file_path = "C:/Users/luyza/saves-lives/saves-lives/frontend/index.html"
    with open(file_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

# Alteração da rota para exibir a página de criação de alertas
@app.get("/alertas/criar", response_class=HTMLResponse)
async def alertas_page():
    file_path = "C:/Users/luyza/saves-lives/saves-lives/frontend/css/js/alertas.html"
    with open(file_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/alertas/lista", response_class=HTMLResponse)
async def alertas_lista_page():
    file_path = "C:/Users/luyza/saves-lives/saves-lives/frontend/css/js/lista_alertas.html"
    with open(file_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
        
# Ponto de entrada principal da aplicação
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
