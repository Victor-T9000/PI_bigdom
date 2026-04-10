from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from utils.database import execute_query

barbeiros_bp = Blueprint('barbeiros', __name__, url_prefix='/api/barbeiros')

@barbeiros_bp.route('', methods=['GET']) 
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

    try:
        # Calcular dia da semana manualmente
        from datetime import datetime
        import datetime as dt_module
        
        # Converter data para objeto datetime
        data_obj = datetime.strptime(data, '%Y-%m-%d')
        dia_semana = data_obj.isoweekday()
        
        print(f"📅 Data: {data}, Dia semana: {dia_semana}")
        
        # Buscar horários do barbeiro
        horarios_trabalho = execute_query("""
            SELECT 
                TIME_FORMAT(hora_inicio, '%H:%i') as hora_inicio,
                TIME_FORMAT(hora_fim, '%H:%i') as hora_fim
            FROM horario_trabalho 
            WHERE id_barbeiro = %s AND dia_semana = %s
        """, (barbeiro_id, dia_semana), fetch_one=True)
        
        print(f"📅 Horários encontrados: {horarios_trabalho}")
        
        if not horarios_trabalho:
            return jsonify({'horarios': []})
        
        # Buscar horários ocupados
        ocupados = execute_query("""
            SELECT DATE_FORMAT(data_agendamento, '%H:%i') as hora
            FROM agendamento_atendimento
            WHERE id_barbeiro = %s AND DATE(data_agendamento) = %s
            AND status IN ('pendente', 'confirmado')
        """, (barbeiro_id, data), fetch_all=True)
        
        horas_ocupadas = [o['hora'] for o in ocupados if o.get('hora')]
        print(f"📅 Horários ocupados: {horas_ocupadas}")
        
        # Gerar slots
        horarios = []
        hora_inicio = horarios_trabalho['hora_inicio']
        hora_fim = horarios_trabalho['hora_fim']
        
        # Converter para minutos
        inicio_min = int(hora_inicio.split(':')[0]) * 60 + int(hora_inicio.split(':')[1])
        fim_min = int(hora_fim.split(':')[0]) * 60 + int(hora_fim.split(':')[1])
        
        for minutos in range(inicio_min, fim_min, 30):
            hora = minutos // 60
            minuto = minutos % 60
            hora_str = f"{hora:02d}:{minuto:02d}"
            horarios.append({
                'hora': hora_str,
                'disponivel': hora_str not in horas_ocupadas
            })
        
        print(f"📅 Gerados {len(horarios)} horários")
        return jsonify({'horarios': horarios})
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        # Fallback
        horarios = []
        for hora in range(9, 18):
            for minuto in [0, 30]:
                hora_str = f"{hora:02d}:{minuto:02d}"
                horarios.append({'hora': hora_str, 'disponivel': True})
        return jsonify({'horarios': horarios})