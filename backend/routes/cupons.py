from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query
from datetime import date

cupons_bp = Blueprint('cupons', __name__, url_prefix='/api/cupons')

@cupons_bp.route('/meus', methods=['GET'])
@token_required
def meus_cupons():
    cupons = execute_query("""
        SELECT * FROM cupom
        WHERE id_cliente = %s AND usado = FALSE AND data_validade >= CURDATE()
        ORDER BY data_validade ASC
    """, (request.user_id,), fetch_all=True)

    return jsonify(cupons)

@cupons_bp.route('/historico', methods=['GET'])
@token_required
def historico_cupons():
    cupons = execute_query("""
        SELECT * FROM cupom
        WHERE id_cliente = %s
        ORDER BY data_geracao DESC
    """, (request.user_id,), fetch_all=True)

    return jsonify(cupons)