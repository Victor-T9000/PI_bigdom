from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/api/avaliacoes')

@relatorios_bp.route('/', methods=['POST'])
@token_required
def criar_avaliacao():
    data = request.json

    if not data.get('id_agendamento'):
        return jsonify({'error': 'ID do agendamento é obrigatório'}), 400

    if not data.get('avaliacao') or data['avaliacao'] < 1 or data['avaliacao'] > 5:
        return jsonify({'error': 'Avaliação deve ser entre 1 e 5'}), 400

    # Verificar se agendamento pertence ao cliente e está concluído
    agendamento = execute_query("""
        SELECT id_agendamento FROM agendamento_atendimento
        WHERE id_agendamento = %s AND id_cliente = %s AND status = 'concluido'
    """, (data['id_agendamento'], request.user_id), fetch_one=True)

    if not agendamento:
        return jsonify({'error': 'Agendamento não encontrado ou não concluído'}), 404

    # Verificar se já existe avaliação
    existing = execute_query("""
        SELECT id_relatorio FROM relatorio_atendimento
        WHERE id_agendamento = %s
    """, (data['id_agendamento'],), fetch_one=True)

    if existing:
        return jsonify({'error': 'Este agendamento já foi avaliado'}), 409

    relatorio_id = execute_query("""
        INSERT INTO relatorio_atendimento (id_agendamento, avaliacao, recomendacoes)
        VALUES (%s, %s, %s)
    """, (data['id_agendamento'], data['avaliacao'], data.get('recomendacoes')), commit=True)

    return jsonify({
        'message': 'Avaliação enviada com sucesso',
        'id_relatorio': relatorio_id
    }), 201

@relatorios_bp.route('/barbeiro/<int:barbeiro_id>', methods=['GET'])
def get_avaliacoes_barbeiro(barbeiro_id):
    avaliacoes = execute_query("""
        SELECT ra.*, c.nome as cliente_nome, s.nome as servico_nome,
               a.data_agendamento
        FROM relatorio_atendimento ra
        JOIN agendamento_atendimento a ON ra.id_agendamento = a.id_agendamento
        JOIN cliente c ON a.id_cliente = c.id_cliente
        JOIN servico s ON a.id_servico = s.id_servico
        WHERE a.id_barbeiro = %s
        ORDER BY ra.data_atendimento DESC
    """, (barbeiro_id,), fetch_all=True)

    return jsonify(avaliacoes)