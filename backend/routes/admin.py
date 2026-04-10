from flask import Blueprint, request, jsonify
from middleware.auth import token_required_admin
from utils.database import execute_query

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# =============================================
# BARBEARIAS PENDENTES
# =============================================

@admin_bp.route('/barbearias/pendentes', methods=['GET'])
@token_required_admin
def listar_barbearias_pendentes():
    """Lista barbearias aguardando aprovação"""
    barbearias = execute_query("""
        SELECT id_barbearia, nome, email, telefone, endereco, cidade, estado, 
               descricao, logo_url, data_cadastro
        FROM barbearia
        WHERE status = 'pendente'
        ORDER BY data_cadastro ASC
    """, fetch_all=True)
    return jsonify(barbearias)


@admin_bp.route('/barbearias/aprovar/<int:barbearia_id>', methods=['PUT'])
@token_required_admin
def aprovar_barbearia(barbearia_id):
    """Aprova uma barbearia pendente"""
    
    # Atualizar status da barbearia
    execute_query("""
        UPDATE barbearia 
        SET status = 'ativa'
        WHERE id_barbearia = %s AND status = 'pendente'
    """, (barbearia_id,), commit=True)
    
    # Atualizar status no usuario também
    execute_query("""
        UPDATE usuario 
        SET status = 'ativo'
        WHERE id_referencia = %s AND tipo = 'barbearia'
    """, (barbearia_id,), commit=True)
    
    return jsonify({'message': 'Barbearia aprovada com sucesso'})


@admin_bp.route('/barbearias/rejeitar/<int:barbearia_id>', methods=['DELETE'])
@token_required_admin
def rejeitar_barbearia(barbearia_id):
    """Rejeita uma barbearia pendente"""
    
    # Obter email para referência
    barbearia = execute_query(
        "SELECT email FROM barbearia WHERE id_barbearia = %s",
        (barbearia_id,), fetch_one=True
    )
    
    # Remover barbearia
    execute_query("DELETE FROM barbearia WHERE id_barbearia = %s", (barbearia_id,), commit=True)
    
    # Remover do usuario
    execute_query("""
        DELETE FROM usuario 
        WHERE id_referencia = %s AND tipo = 'barbearia'
    """, (barbearia_id,), commit=True)
    
    return jsonify({'message': 'Barbearia rejeitada e removida'})


# =============================================
# LISTAR TODAS BARBEARIAS (ADMIN)
# =============================================

@admin_bp.route('/barbearias', methods=['GET'])
@token_required_admin
def listar_todas_barbearias():
    """Lista todas as barbearias (para admin)"""
    barbearias = execute_query("""
        SELECT id_barbearia, nome, email, telefone, endereco, cidade, estado, 
               status, data_cadastro,
               (SELECT COUNT(*) FROM barbeiro WHERE id_barbearia = b.id_barbearia) as total_barbeiros,
               (SELECT COUNT(*) FROM servico WHERE id_barbearia = b.id_barbearia) as total_servicos
        FROM barbearia b
        ORDER BY data_cadastro DESC
    """, fetch_all=True)
    return jsonify(barbearias)


# =============================================
# ESTATÍSTICAS GERAIS (ADMIN)
# =============================================

@admin_bp.route('/estatisticas', methods=['GET'])
@token_required_admin
def get_estatisticas():
    """Retorna estatísticas gerais do sistema"""
    
    total_barbearias = execute_query("SELECT COUNT(*) as total FROM barbearia", fetch_one=True)
    total_barbeiros = execute_query("SELECT COUNT(*) as total FROM barbeiro", fetch_one=True)
    total_clientes = execute_query("SELECT COUNT(*) as total FROM cliente", fetch_one=True)
    total_agendamentos = execute_query("SELECT COUNT(*) as total FROM agendamento_atendimento", fetch_one=True)
    pendentes = execute_query("SELECT COUNT(*) as total FROM barbearia WHERE status = 'pendente'", fetch_one=True)
    
    # Agendamentos por mês (últimos 6 meses)
    agendamentos_mensal = execute_query("""
        SELECT DATE_FORMAT(data_agendamento, '%Y-%m') as mes, COUNT(*) as total
        FROM agendamento_atendimento
        WHERE data_agendamento >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(data_agendamento, '%Y-%m')
        ORDER BY mes DESC
    """, fetch_all=True)
    
    return jsonify({
        'total_barbearias': total_barbearias['total'] if total_barbearias else 0,
        'total_barbeiros': total_barbeiros['total'] if total_barbeiros else 0,
        'total_clientes': total_clientes['total'] if total_clientes else 0,
        'total_agendamentos': total_agendamentos['total'] if total_agendamentos else 0,
        'pendentes': pendentes['total'] if pendentes else 0,
        'agendamentos_mensal': agendamentos_mensal
    })