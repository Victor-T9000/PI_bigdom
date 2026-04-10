from flask import Blueprint, request, jsonify
from middleware.auth import token_required_barbearia
from utils.database import execute_query
from datetime import datetime

barbearia_dashboard_bp = Blueprint('barbearia_dashboard', __name__, url_prefix='/api/barbearia')

# =============================================
# DASHBOARD - INFORMAÇÕES GERAIS
# =============================================

@barbearia_dashboard_bp.route('/dashboard', methods=['GET'])
@token_required_barbearia
def get_dashboard_info():
    """Retorna informações gerais para o dashboard"""
    
    # Total de barbeiros
    total_barbeiros = execute_query("""
        SELECT COUNT(*) as total FROM barbeiro 
        WHERE id_barbearia = %s AND status = 'ativo'
    """, (request.barbearia_id,), fetch_one=True)
    
    # Total de serviços
    total_servicos = execute_query("""
        SELECT COUNT(*) as total FROM servico 
        WHERE id_barbearia = %s AND status = 'ativo'
    """, (request.barbearia_id,), fetch_one=True)
    
    # Agendamentos de hoje
    agendamentos_hoje = execute_query("""
        SELECT COUNT(*) as total FROM agendamento_atendimento a
        JOIN barbeiro b ON a.id_barbeiro = b.id_barbeiro
        WHERE b.id_barbearia = %s AND DATE(a.data_agendamento) = CURDATE()
    """, (request.barbearia_id,), fetch_one=True)
    
    # Agendamentos pendentes
    agendamentos_pendentes = execute_query("""
        SELECT COUNT(*) as total FROM agendamento_atendimento a
        JOIN barbeiro b ON a.id_barbeiro = b.id_barbeiro
        WHERE b.id_barbearia = %s AND a.status = 'pendente'
    """, (request.barbearia_id,), fetch_one=True)
    
    return jsonify({
        'total_barbeiros': total_barbeiros['total'] if total_barbeiros else 0,
        'total_servicos': total_servicos['total'] if total_servicos else 0,
        'agendamentos_hoje': agendamentos_hoje['total'] if agendamentos_hoje else 0,
        'agendamentos_pendentes': agendamentos_pendentes['total'] if agendamentos_pendentes else 0
    })


# =============================================
# BARBEIROS - CRUD COMPLETO
# =============================================

@barbearia_dashboard_bp.route('/barbeiros', methods=['GET'])
@token_required_barbearia
def listar_barbeiros():
    """Lista todos os barbeiros da barbearia"""
    barbeiros = execute_query("""
        SELECT b.*, 
               (SELECT COUNT(*) FROM agendamento_atendimento WHERE id_barbeiro = b.id_barbeiro AND status = 'concluido') as total_atendimentos
        FROM barbeiro b
        WHERE b.id_barbearia = %s AND b.status = 'ativo'
        ORDER BY b.nome
    """, (request.barbearia_id,), fetch_all=True)
    return jsonify(barbeiros)


@barbearia_dashboard_bp.route('/barbeiros', methods=['POST'])
@token_required_barbearia
def cadastrar_barbeiro():
    """Cadastra um novo barbeiro"""
    data = request.json

    required = ['nome', 'email', 'telefone']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    # Verificar se email já existe
    existing = execute_query(
        "SELECT id_barbeiro FROM barbeiro WHERE email = %s",
        (data['email'],),
        fetch_one=True
    )

    if existing:
        return jsonify({'error': 'Email já cadastrado'}), 409

    barbeiro_id = execute_query("""
        INSERT INTO barbeiro (id_barbearia, nome, email, telefone, especialidade, foto_url, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'ativo')
    """, (
        request.barbearia_id, 
        data['nome'], 
        data['email'], 
        data['telefone'],
        data.get('especialidade'), 
        data.get('foto_url')
    ), commit=True)

    return jsonify({
        'message': 'Barbeiro cadastrado com sucesso', 
        'id_barbeiro': barbeiro_id
    }), 201


@barbearia_dashboard_bp.route('/barbeiros/<int:barbeiro_id>', methods=['PUT'])
@token_required_barbearia
def atualizar_barbeiro(barbeiro_id):
    """Atualiza dados de um barbeiro"""
    data = request.json

    # Verificar se barbeiro pertence à barbearia
    barbeiro = execute_query("""
        SELECT id_barbeiro FROM barbeiro 
        WHERE id_barbeiro = %s AND id_barbearia = %s
    """, (barbeiro_id, request.barbearia_id), fetch_one=True)

    if not barbeiro:
        return jsonify({'error': 'Barbeiro não encontrado'}), 404

    execute_query("""
        UPDATE barbeiro 
        SET nome = %s, telefone = %s, especialidade = %s, foto_url = %s
        WHERE id_barbeiro = %s
    """, (
        data.get('nome'), 
        data.get('telefone'),
        data.get('especialidade'), 
        data.get('foto_url'),
        barbeiro_id
    ), commit=True)

    return jsonify({'message': 'Barbeiro atualizado com sucesso'})


@barbearia_dashboard_bp.route('/barbeiros/<int:barbeiro_id>', methods=['DELETE'])
@token_required_barbearia
def deletar_barbeiro(barbeiro_id):
    """Remove (inativa) um barbeiro"""
    # Verificar se barbeiro pertence à barbearia
    barbeiro = execute_query("""
        SELECT id_barbeiro FROM barbeiro 
        WHERE id_barbeiro = %s AND id_barbearia = %s
    """, (barbeiro_id, request.barbearia_id), fetch_one=True)

    if not barbeiro:
        return jsonify({'error': 'Barbeiro não encontrado'}), 404

    execute_query("""
        UPDATE barbeiro SET status = 'inativo'
        WHERE id_barbeiro = %s
    """, (barbeiro_id,), commit=True)

    return jsonify({'message': 'Barbeiro removido com sucesso'})


# =============================================
# SERVIÇOS - CRUD COMPLETO
# =============================================

@barbearia_dashboard_bp.route('/servicos', methods=['GET'])
@token_required_barbearia
def listar_servicos():
    """Lista todos os serviços da barbearia"""
    servicos = execute_query("""
        SELECT * FROM servico 
        WHERE id_barbearia = %s AND status = 'ativo'
        ORDER BY nome
    """, (request.barbearia_id,), fetch_all=True)
    return jsonify(servicos)


@barbearia_dashboard_bp.route('/servicos', methods=['POST'])
@token_required_barbearia
def cadastrar_servico():
    """Cadastra um novo serviço"""
    data = request.json

    required = ['nome', 'preco']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    servico_id = execute_query("""
        INSERT INTO servico (id_barbearia, nome, descricao, preco, duracao_minutos, categoria, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'ativo')
    """, (
        request.barbearia_id, 
        data['nome'], 
        data.get('descricao'), 
        data['preco'],
        data.get('duracao_minutos', 30), 
        data.get('categoria')
    ), commit=True)

    return jsonify({
        'message': 'Serviço cadastrado com sucesso', 
        'id_servico': servico_id
    }), 201


@barbearia_dashboard_bp.route('/servicos/<int:servico_id>', methods=['PUT'])
@token_required_barbearia
def atualizar_servico(servico_id):
    """Atualiza um serviço"""
    data = request.json

    # Verificar se serviço pertence à barbearia
    servico = execute_query("""
        SELECT id_servico FROM servico 
        WHERE id_servico = %s AND id_barbearia = %s
    """, (servico_id, request.barbearia_id), fetch_one=True)

    if not servico:
        return jsonify({'error': 'Serviço não encontrado'}), 404

    execute_query("""
        UPDATE servico 
        SET nome = %s, descricao = %s, preco = %s, duracao_minutos = %s, categoria = %s
        WHERE id_servico = %s
    """, (
        data.get('nome'), 
        data.get('descricao'), 
        data.get('preco'),
        data.get('duracao_minutos'), 
        data.get('categoria'),
        servico_id
    ), commit=True)

    return jsonify({'message': 'Serviço atualizado com sucesso'})


@barbearia_dashboard_bp.route('/servicos/<int:servico_id>', methods=['DELETE'])
@token_required_barbearia
def deletar_servico(servico_id):
    """Remove (inativa) um serviço"""
    servico = execute_query("""
        SELECT id_servico FROM servico 
        WHERE id_servico = %s AND id_barbearia = %s
    """, (servico_id, request.barbearia_id), fetch_one=True)

    if not servico:
        return jsonify({'error': 'Serviço não encontrado'}), 404

    execute_query("""
        UPDATE servico SET status = 'inativo'
        WHERE id_servico = %s
    """, (servico_id,), commit=True)

    return jsonify({'message': 'Serviço removido com sucesso'})


# =============================================
# HORÁRIOS DE TRABALHO
# =============================================

@barbearia_dashboard_bp.route('/barbeiros/<int:barbeiro_id>/horarios', methods=['GET'])
@token_required_barbearia
def get_horarios_barbeiro(barbeiro_id):
    """Retorna os horários de trabalho de um barbeiro"""
    horarios = execute_query("""
        SELECT * FROM horario_trabalho
        WHERE id_barbeiro = %s
        ORDER BY dia_semana, hora_inicio
    """, (barbeiro_id,), fetch_all=True)
    return jsonify(horarios)


@barbearia_dashboard_bp.route('/barbeiros/<int:barbeiro_id>/horarios', methods=['POST'])
@token_required_barbearia
def adicionar_horario(barbeiro_id):
    """Adiciona um horário de trabalho para um barbeiro"""
    data = request.json

    required = ['dia_semana', 'hora_inicio', 'hora_fim']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400

    # Verificar se barbeiro pertence à barbearia
    barbeiro = execute_query("""
        SELECT id_barbeiro FROM barbeiro 
        WHERE id_barbeiro = %s AND id_barbearia = %s
    """, (barbeiro_id, request.barbearia_id), fetch_one=True)

    if not barbeiro:
        return jsonify({'error': 'Barbeiro não encontrado'}), 404

    execute_query("""
        INSERT INTO horario_trabalho (id_barbeiro, dia_semana, hora_inicio, hora_fim)
        VALUES (%s, %s, %s, %s)
    """, (barbeiro_id, data['dia_semana'], data['hora_inicio'], data['hora_fim']), commit=True)

    return jsonify({'message': 'Horário adicionado com sucesso'}), 201


@barbearia_dashboard_bp.route('/horarios/<int:horario_id>', methods=['DELETE'])
@token_required_barbearia
def remover_horario(horario_id):
    """Remove um horário de trabalho"""
    execute_query("""
        DELETE FROM horario_trabalho WHERE id_horario = %s
    """, (horario_id,), commit=True)

    return jsonify({'message': 'Horário removido com sucesso'})


# =============================================
# AGENDAMENTOS
# =============================================

@barbearia_dashboard_bp.route('/agendamentos', methods=['GET'])
@token_required_barbearia
def listar_agendamentos():
    """Lista todos os agendamentos da barbearia"""
    status_filter = request.args.get('status')
    data_filter = request.args.get('data')
    
    query = """
        SELECT a.*, 
               c.nome as cliente_nome, 
               c.telefone as cliente_telefone,
               c.email as cliente_email,
               b.nome as barbeiro_nome, 
               s.nome as servico_nome,
               s.preco
        FROM agendamento_atendimento a
        JOIN barbeiro b ON a.id_barbeiro = b.id_barbeiro
        JOIN servico s ON a.id_servico = s.id_servico
        JOIN cliente c ON a.id_cliente = c.id_cliente
        WHERE b.id_barbearia = %s
    """
    params = [request.barbearia_id]
    
    if status_filter:
        query += " AND a.status = %s"
        params.append(status_filter)
    
    if data_filter:
        query += " AND DATE(a.data_agendamento) = %s"
        params.append(data_filter)
    
    query += " ORDER BY a.data_agendamento DESC"
    
    agendamentos = execute_query(query, tuple(params), fetch_all=True)
    return jsonify(agendamentos)


@barbearia_dashboard_bp.route('/agendamentos/<int:agendamento_id>/status', methods=['PUT'])
@token_required_barbearia
def atualizar_status_agendamento(agendamento_id):
    """Atualiza o status de um agendamento"""
    data = request.json
    novo_status = data.get('status')
    
    status_validos = ['pendente', 'confirmado', 'cancelado', 'concluido']
    if novo_status not in status_validos:
        return jsonify({'error': 'Status inválido'}), 400
    
    execute_query("""
        UPDATE agendamento_atendimento a
        JOIN barbeiro b ON a.id_barbeiro = b.id_barbeiro
        SET a.status = %s
        WHERE a.id_agendamento = %s AND b.id_barbearia = %s
    """, (novo_status, agendamento_id, request.barbearia_id), commit=True)
    
    return jsonify({'message': f'Status atualizado para {novo_status}'})