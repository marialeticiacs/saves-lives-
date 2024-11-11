from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # Configurações da aplicação
    app.config['SECRET_KEY'] = 'minha-chave-secreta'  
    app.config['WEATHERBIT_API_KEY'] = os.getenv('WEATHERBIT_API_KEY', 'd9c0bac411174df994d49f8009d1bf72')


    # Importar e registrar as rotas
    from .routes import main
    app.register_blueprint(main)

    return app
