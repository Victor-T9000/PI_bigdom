from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from config import Config
from routes import register_routes
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.url_map.strict_slashes = False

# CORS configurado corretamente
CORS(app, 
     origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:5000', '*'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
     allow_headers=['Content-Type', 'Authorization', 'Accept', 'X-Requested-With'],
     expose_headers=['Content-Type', 'Authorization'],
     supports_credentials=True,
     max_age=3600)

# Registrar rotas da API
register_routes(app)

# =============================================
# ROTAS PARA PÁGINAS (TEMPLATES)
# =============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro_page():
    return render_template('cadastro.html')

@app.route('/login-admin')
def login_admin_page():
    return render_template('login-admin.html')

@app.route('/login-barbearia')
def login_barbearia_page():
    return render_template('login-barbearia.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin-dashboard.html')

@app.route('/admin/pendentes')
def admin_pendentes():
    return render_template('admin-pendentes.html')

@app.route('/dashboard-barbearia')
def dashboard_barbearia():
    return render_template('dashboard-barbearia.html')

@app.route('/dashboard-barbeiros')
def dashboard_barbeiros():
    return render_template('dashboard-barbeiros.html')

@app.route('/dashboard-servicos')
def dashboard_servicos():
    return render_template('dashboard-servicos.html')

@app.route('/dashboard-agendamentos')
def dashboard_agendamentos():
    return render_template('dashboard-agendamentos.html')

@app.route('/dashboard-horarios')
def dashboard_horarios():
    return render_template('dashboard-horarios.html')

@app.route('/barbearias')
def barbearias_page():
    return render_template('barbearias.html')

@app.route('/barbearia-detalhe')
def barbearia_detalhe_page():
    return render_template('barbearia-detalhe.html')

@app.route('/agendamento')
def agendamento_page():
    return render_template('agendamento.html')

@app.route('/meus-agendamentos')
def meus_agendamentos_page():
    return render_template('meus-agendamentos.html')

@app.route('/galeria')
def galeria_page():
    return render_template('galeria.html')

@app.route('/cupons')
def cupons_page():
    return render_template('cupons.html')

@app.route('/perfil')
def perfil_page():
    return render_template('perfil.html')

# Servir arquivos estáticos
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')