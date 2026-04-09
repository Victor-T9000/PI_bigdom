from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from config import Config
from routes import register_routes
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='/static')
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = Config.SECRET_KEY

# CORS completo para desenvolvimento
CORS(app, 
     origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:5000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Accept'],
     supports_credentials=True)

# Registrar rotas da API
register_routes(app)

# Servir arquivos estáticos (CSS, JS)
@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('../frontend/css', path)

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('../frontend/js', path)

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('../frontend/assets', path)

# Servir páginas HTML
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>.html')
def serve_html(filename):
    return send_from_directory('../frontend', f'{filename}.html')

# Tratamento de erro 404
@app.errorhandler(404)
def page_not_found(e):
    # Se for uma requisição de API, retorna JSON
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Rota não encontrada'}), 404
    # Senão, tenta servir o index.html
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    print(f"🚀 Servidor rodando em http://localhost:5000")
    print(f"📁 Frontend disponível em http://localhost:5000")
    app.run(debug=True, port=5000)  # SEM host='0.0.0.0'