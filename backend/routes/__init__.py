from routes.auth import auth_bp
from routes.barbearias import barbearias_bp
from routes.barbeiros import barbeiros_bp
from routes.servicos import servicos_bp
from routes.agendamentos import agendamentos_bp
from routes.relatorios import relatorios_bp
from routes.cupons import cupons_bp
from routes.galeria import galeria_bp
from routes.barbearia_dashboard import barbearia_dashboard_bp
from routes.admin import admin_bp  # ← NOVO

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(barbearias_bp)
    app.register_blueprint(barbeiros_bp)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(agendamentos_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(cupons_bp)
    app.register_blueprint(galeria_bp)
    app.register_blueprint(barbearia_dashboard_bp)
    app.register_blueprint(admin_bp)  # ← NOVO