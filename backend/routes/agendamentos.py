from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query
from datetime import datetime

agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/api/agendamentos')

@agendamentos_bp.route('/', methods=['POST'])
@token_required
def criar_agendamento():
    data = request.json

    required = ['id_barbeiro', 'id_servico', 'data_agendamento']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    # Verificar se horário está disponível
    agendamento_existente = execute_query("""
        SELECT id_agendamento FROM agendamento_atendimento
        WHERE id_barbeiro = %s AND data_agendamento = %s
        AND status IN ('pendente', 'confirmado')
    """, (data['id_barbeiro'], data['data_agendamento']), fetch_one=True)

    if agendamento_existente:
        return jsonify({'error': 'Horário já ocupado'}), 409

    # Buscar preço do serviço
    servico = execute_query(
        "SELECT preco FROM servico WHERE id_servico = %s",
        (data['id_servico'],),
        fetch_one=True
    )

    agendamento_id = execute_query("""
        INSERT INTO agendamento_atendimento (id_cliente, id_barbeiro, id_servico, data_agendamento, status, observacao)
        VALUES (%s, %s, %s, %s, 'pendente', %s)
    """, (
        request.user_id, data['id_barbeiro'], data['id_servico'],
        data['data_agendamento'], data.get('observacao')
    ), commit=True)

    return jsonify({
        'message': 'Agendamento criado com sucesso',
        'id_agendamento': agendamento_id
    }), 201

@agendamentos_bp.route('/meus', methods=['GET'])
@token_required
def meus_agendamentos():
    agendamentos = execute_query("""
        SELECT a.*, b.nome as barbeiro_nome, s.nome as servico_nome, s.preco,
               br.nome as barbearia_nome
        FROM agendamento_atendimento a
        JOIN barbeiro b ON a.id_barbeiro = b.id_barbeiro
        JOIN servico s ON a.id_servico = s.id_servico
        JOIN barbearia br ON b.id_barbearia = br.id_barbearia
        WHERE a.id_cliente = %s
        ORDER BY a.data_agendamento DESC
    """, (request.user_id,), fetch_all=True)

    return jsonify(agendamentos)

@agendamentos_bp.route('/<int:agendamento_id>', methods=['PUT'])
@token_required
def atualizar_agendamento(agendamento_id):
    data = request.json

    # Verificar se agendamento pertence ao cliente
    agendamento = execute_query("""
        SELECT id_agendamento, status FROM agendamento_atendimento
        WHERE id_agendamento = %s AND id_cliente = %s
    """, (agendamento_id, request.user_id), fetch_one=True)

    if not agendamento:
        return jsonify({'error': 'Agendamento não encontrado'}), 404

    if agendamento['status'] == 'cancelado':
        return jsonify({'error': 'Agendamento já cancelado'}), 400

    if agendamento['status'] == 'concluido':
        return jsonify({'error': 'Agendamento já concluído'}), 400

    if data.get('data_agendamento'):
        execute_query("""
            UPDATE agendamento_atendimento
            SET data_agendamento = %s
            WHERE id_agendamento = %s
        """, (data['data_agendamento'], agendamento_id), commit=True)

    if data.get('status') == 'cancelado':
        execute_query("""
            UPDATE agendamento_atendimento
            SET status = 'cancelado'
            WHERE id_agendamento = %s
        """, (agendamento_id,), commit=True)
        return jsonify({'message': 'Agendamento cancelado com sucesso'})

    return jsonify({'message': 'Agendamento atualizado com sucesso'})

@agendamentos_bp.route('/<int:agendamento_id>', methods=['DELETE'])
@token_required
def cancelar_agendamento(agendamento_id):
    agendamento = execute_query("""
        SELECT id_agendamento, status FROM agendamento_atendimento
        WHERE id_agendamento = %s AND id_cliente = %s
    """, (agendamento_id, request.user_id), fetch_one=True)

    if not agendamento:
        return jsonify({'error': 'Agendamento não encontrado'}), 404

    if agendamento['status'] == 'cancelado':
        return jsonify({'error': 'Agendamento já cancelado'}), 400

    execute_query("""
        UPDATE agendamento_atendimento
        SET status = 'cancelado'
        WHERE id_agendamento = %s
    """, (agendamento_id,), commit=True)

    return jsonify({'message': 'Agendamento cancelado com sucesso'})