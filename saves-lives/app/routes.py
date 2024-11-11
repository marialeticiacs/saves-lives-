from flask import Blueprint, request, jsonify, current_app, render_template
import requests

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')  # Renderiza o template HTML para a página inicial

@main.route('/weather/alerts', methods=['GET'])
def obter_alertas_climaticos():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not lat or not lon:
        return jsonify({"error": "Parâmetros 'lat' e 'lon' são obrigatórios"}), 400

    api_key = current_app.config['WEATHERBIT_API_KEY']
    url = f"https://api.weatherbit.io/v2.0/alerts?lat={lat}&lon={lon}&key={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Não foi possível obter os alertas climáticos"}), response.status_code

    data = response.json()
    alerts = data.get('alerts', [])

    if not alerts:
        return jsonify({"message": "Nenhum alerta ativo no momento para esta região."})

    return jsonify({"alerts": alerts})