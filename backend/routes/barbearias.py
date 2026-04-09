from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query

barbearias_bp = Blueprint('barbearias', __name__, url_prefix='/api/barbearias')

# CORRIGIDO: remova a barra '/'
@barbearias_bp.route('', methods=['GET'])  # ← sem barra
def listar_barbearias():
    cidade = request.args.get('cidade')
    busca = request.args.get('busca')

    query = "SELECT * FROM barbearia WHERE status = 'ativa'"
    params = []

    if cidade:
        query += " AND cidade = %s"
        params.append(cidade)

    if busca:
        query += " AND (nome LIKE %s OR endereco LIKE %s)"
        params.extend([f'%{busca}%', f'%{busca}%'])

    barbearias = execute_query(query, tuple(params), fetch_all=True)
    return jsonify(barbearias)

@barbearias_bp.route('/<int:barbearia_id>', methods=['GET'])
def get_barbearia(barbearia_id):
    barbearia = execute_query(
        "SELECT * FROM barbearia WHERE id_barbearia = %s",
        (barbearia_id,),
        fetch_one=True
    )

    if not barbearia:
        return jsonify({'error': 'Barbearia não encontrada'}), 404

    return jsonify(barbearia)

# CORRIGIDO: também remova a barra aqui
@barbearias_bp.route('', methods=['POST'])  # ← sem barra
def cadastrar_barbearia():
    data = request.json

    required = ['nome', 'email', 'telefone', 'endereco', 'cidade', 'estado']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    # Verificar se email já existe
    existing = execute_query(
        "SELECT id_barbearia FROM barbearia WHERE email = %s",
        (data['email'],),
        fetch_one=True
    )

    if existing:
        return jsonify({'error': 'Email já cadastrado'}), 409

    barbearia_id = execute_query("""
        INSERT INTO barbearia (nome, email, telefone, endereco, cidade, estado, cep, descricao, logo_url, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pendente')
    """, (
        data['nome'], data['email'], data['telefone'], data['endereco'],
        data['cidade'], data['estado'], data.get('cep'), data.get('descricao'), data.get('logo_url')
    ), commit=True)

    return jsonify({'message': 'Barbearia cadastrada com sucesso', 'id_barbearia': barbearia_id}), 201