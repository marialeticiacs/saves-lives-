import requests
import csv
from typing import List, Dict

def buscar_dados_queimadas() -> List[Dict]:
    url = "https://queimadas.dgi.inpe.br/queimadas/arquivos/dados_abertos/versao_1/focos_abertos_24h.csv"
    response = requests.get(url, verify=False)  # Ignora verificação SSL
    
    if response.status_code == 200:
        # Salva o conteúdo do CSV temporariamente
        with open("focos_queimadas.csv", "w", newline='', encoding='utf-8') as f:
            f.write(response.text)
        print("Dados de queimadas atualizados.")
        
        # Processa o arquivo CSV
        focos = []
        with open("focos_queimadas.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                focos.append({
                    "estado": row["estado"],
                    "municipio": row["municipio"],
                    "latitude": row["lat"],
                    "longitude": row["lon"],
                    "risco_fogo": row["risco_fogo"],
                    "data": row["data_hora_gmt"]
                })
        return focos
    else:
        print("Erro ao baixar dados do INPE")
        return []

# Exemplo de uso
if __name__ == "__main__":
    focos_queimadas = buscar_dados_queimadas()
    for foco in focos_queimadas[:5]:  # Exibe apenas os primeiros 5 para teste
        print(foco)
