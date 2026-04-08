from flask import Blueprint, request, jsonify
from utils.database import execute_query

galeria_bp = Blueprint('galeria', __name__, url_prefix='/api/galeria')

@galeria_bp.route('/', methods=['GET'])
def listar_galeria():
    barbearia_id = request.args.get('barbearia_id')
    barbeiro_id = request.args.get('barbeiro_id')
    destaque = request.args.get('destaque')

    query = "SELECT * FROM galeria WHERE 1=1"
    params = []

    if barbearia_id:
        query += " AND id_barbearia = %s"
        params.append(barbearia_id)

    if barbeiro_id:
        query += " AND id_barbeiro = %s"
        params.append(barbeiro_id)

    if destaque == 'true':
        query += " AND destaque = TRUE"

    query += " ORDER BY data_upload DESC"

    galeria = execute_query(query, tuple(params), fetch_all=True)
    return jsonify(galeria)

@galeria_bp.route('/<int:galeria_id>', methods=['GET'])
def get_midia(galeria_id):
    midia = execute_query(
        "SELECT * FROM galeria WHERE id_galeria = %s",
        (galeria_id,),
        fetch_one=True
    )

    if not midia:
        return jsonify({'error': 'Mídia não encontrada'}), 404

    # Incrementar visualizações
    execute_query(
        "UPDATE galeria SET visualizacoes = visualizacoes + 1 WHERE id_galeria = %s",
        (galeria_id,),
        commit=True
    )

    return jsonify(midia)