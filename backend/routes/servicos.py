from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query

servicos_bp = Blueprint('servicos', __name__, url_prefix='/api/servicos')

@servicos_bp.route('/', methods=['GET'])
def listar_servicos():
    barbearia_id = request.args.get('barbearia_id')
    categoria = request.args.get('categoria')

    query = "SELECT * FROM servico WHERE status = 'ativo'"
    params = []

    if barbearia_id:
        query += " AND id_barbearia = %s"
        params.append(barbearia_id)

    if categoria:
        query += " AND categoria = %s"
        params.append(categoria)

    servicos = execute_query(query, tuple(params), fetch_all=True)
    return jsonify(servicos)

@servicos_bp.route('/<int:servico_id>', methods=['GET'])
def get_servico(servico_id):
    servico = execute_query(
        "SELECT * FROM servico WHERE id_servico = %s",
        (servico_id,),
        fetch_one=True
    )

    if not servico:
        return jsonify({'error': 'Serviço não encontrado'}), 404

    return jsonify(servico)