from flask import Flask
from flask_cors import CORS
from config import Config
from routes import register_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# CORS completo para desenvolvimento
CORS(app, 
     origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'null', '*'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Accept'],
     supports_credentials=True)

# Registrar rotas
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')