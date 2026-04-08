from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query

barbeiros_bp = Blueprint('barbeiros', __name__, url_prefix='/api/barbeiros')

@barbeiros_bp.route('/', methods=['GET'])
def listar_barbeiros():
    barbearia_id = request.args.get('barbearia_id')
    servico_id = request.args.get('servico_id')

    query = """
        SELECT b.*, br.nome as barbearia_nome
        FROM barbeiro b
        JOIN barbearia br ON b.id_barbearia = br.id_barbearia
        WHERE b.status = 'ativo'
    """
    params = []

    if barbearia_id:
        query += " AND b.id_barbearia = %s"
        params.append(barbearia_id)

    if servico_id:
        query += """
            AND b.id_barbeiro IN (
                SELECT id_barbeiro FROM barbeiro_servico WHERE id_servico = %s
            )
        """
        params.append(servico_id)

    barbeiros = execute_query(query, tuple(params), fetch_all=True)
    return jsonify(barbeiros)

@barbeiros_bp.route('/<int:barbeiro_id>', methods=['GET'])
def get_barbeiro(barbeiro_id):
    barbeiro = execute_query("""
        SELECT b.*, br.nome as barbearia_nome, br.cidade, br.estado
        FROM barbeiro b
        JOIN barbearia br ON b.id_barbearia = br.id_barbearia
        WHERE b.id_barbeiro = %s
    """, (barbeiro_id,), fetch_one=True)

    if not barbeiro:
        return jsonify({'error': 'Barbeiro não encontrado'}), 404

    # Buscar serviços que o barbeiro oferece
    servicos = execute_query("""
        SELECT s.* FROM servico s
        JOIN barbeiro_servico bs ON s.id_servico = bs.id_servico
        WHERE bs.id_barbeiro = %s AND s.status = 'ativo'
    """, (barbeiro_id,), fetch_all=True)

    barbeiro['servicos'] = servicos

    return jsonify(barbeiro)

@barbeiros_bp.route('/<int:barbeiro_id>/horarios', methods=['GET'])
def get_horarios(barbeiro_id):
    data = request.args.get('data')

    if not data:
        return jsonify({'error': 'Data é obrigatória'}), 400

    # Buscar horários de trabalho do barbeiro
    dia_semana = None  # Calcular baseado na data
    from datetime import datetime
    dia_semana = datetime.strptime(data, '%Y-%m-%d').weekday() + 1  # 1=Segunda, 6=Sábado, 7=Domingo

    horarios_trabalho = execute_query("""
        SELECT hora_inicio, hora_fim FROM horario_trabalho
        WHERE id_barbeiro = %s AND dia_semana = %s
    """, (barbeiro_id, dia_semana), fetch_one=True)

    if not horarios_trabalho:
        return jsonify({'horarios': []})

    # Buscar horários já ocupados
    ocupados = execute_query("""
        SELECT TIME(data_agendamento) as hora
        FROM agendamento_atendimento
        WHERE id_barbeiro = %s AND DATE(data_agendamento) = %s
        AND status IN ('pendente', 'confirmado')
    """, (barbeiro_id, data), fetch_all=True)

    horas_ocupadas = [o['hora'].strftime('%H:%M') for o in ocupados]

    # Gerar slots de 30 em 30 minutos
    from datetime import datetime as dt
    hora_inicio = dt.strptime(str(horarios_trabalho['hora_inicio']), '%H:%M:%S')
    hora_fim = dt.strptime(str(horarios_trabalho['hora_fim']), '%H:%M:%S')

    horarios = []
    current = hora_inicio
    while current < hora_fim:
        hora_str = current.strftime('%H:%M')
        horarios.append({
            'hora': hora_str,
            'disponivel': hora_str not in horas_ocupadas
        })
        current = dt.combine(dt.today(), current) + __import__('datetime').timedelta(minutes=30)
        current = current.time()

    return jsonify({'horarios': horarios})