
let barbeariaAtual = null;

// Carregar dados do dashboard
async function carregarDashboard() {
    mostrarLoading(true);
    
    try {
        // Carregar informações da barbearia
        const user = JSON.parse(localStorage.getItem('elbigdom_user') || '{}');
        barbeariaAtual = user;
        document.getElementById('barbearia-nome').textContent = user.nome || 'Barbearia';
        
        // Carregar estatísticas
        const stats = await fetch('/api/barbearia/dashboard', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        const statsData = await stats.json();
        
        document.getElementById('total-barbeiros').textContent = statsData.total_barbeiros || 0;
        document.getElementById('total-servicos').textContent = statsData.total_servicos || 0;
        document.getElementById('agendamentos-hoje').textContent = statsData.agendamentos_hoje || 0;
        document.getElementById('agendamentos-pendentes').textContent = statsData.agendamentos_pendentes || 0;
        
        // Carregar agendamentos de hoje
        await carregarAgendamentosHoje();
        
        // Carregar últimos agendamentos
        await carregarUltimosAgendamentos();
        
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        mostrarMensagem('Erro ao carregar dados do dashboard', 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Carregar agendamentos de hoje
async function carregarAgendamentosHoje() {
    const container = document.getElementById('agendamentos-hoje-lista');
    
    try {
        const hoje = new Date().toISOString().split('T')[0];
        const response = await fetch(`/api/barbearia/agendamentos?data=${hoje}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        const agendamentos = await response.json();
        
        if (agendamentos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="emoji">📭</div>
                    <p>Nenhum agendamento para hoje</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = agendamentos.map(ag => renderAgendamentoItem(ag)).join('');
        
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><p>Erro ao carregar agendamentos</p></div>';
    }
}

// Carregar últimos agendamentos
async function carregarUltimosAgendamentos() {
    const container = document.getElementById('ultimos-agendamentos');
    
    try {
        const response = await fetch('/api/barbearia/agendamentos', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        const agendamentos = await response.json();
        
        if (agendamentos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="emoji">📋</div>
                    <p>Nenhum agendamento encontrado</p>
                </div>
            `;
            return;
        }
        
        // Mostrar apenas os últimos 5
        const ultimos = agendamentos.slice(0, 5);
        container.innerHTML = ultimos.map(ag => renderAgendamentoItem(ag)).join('');
        
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><p>Erro ao carregar agendamentos</p></div>';
    }
}

// Renderizar um item de agendamento
function renderAgendamentoItem(ag) {
    const dataHora = new Date(ag.data_agendamento);
    const hora = dataHora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    const data = dataHora.toLocaleDateString('pt-BR');
    
    const statusClass = getStatusClass(ag.status);
    const statusText = getStatusText(ag.status);
    
    return `
        <div class="agendamento-item">
            <div class="agendamento-info">
                <div class="agendamento-cliente">
                    ${ag.cliente_nome || 'Cliente'}
                </div>
                <div class="agendamento-detalhes">
                    <span>📅 ${data}</span>
                    <span>⏰ ${hora}</span>
                    <span>✂️ ${ag.servico_nome || 'Serviço'}</span>
                    <span>💈 ${ag.barbeiro_nome || 'Barbeiro'}</span>
                    <span>📞 ${ag.cliente_telefone || 'Sem telefone'}</span>
                </div>
            </div>
            <div class="agendamento-actions">
                <span class="agendamento-status ${statusClass}">${statusText}</span>
                ${ag.status === 'pendente' ? `
                    <button class="btn-small btn-success" onclick="atualizarStatus(${ag.id_agendamento}, 'confirmado')">✓ Confirmar</button>
                    <button class="btn-small btn-danger" onclick="atualizarStatus(${ag.id_agendamento}, 'cancelado')">✗ Cancelar</button>
                ` : ''}
                ${ag.status === 'confirmado' ? `
                    <button class="btn-small btn-success" onclick="atualizarStatus(${ag.id_agendamento}, 'concluido')">✓ Concluir</button>
                ` : ''}
            </div>
        </div>
    `;
}

function getStatusClass(status) {
    const classes = {
        'pendente': 'status-pendente',
        'confirmado': 'status-confirmado',
        'concluido': 'status-concluido',
        'cancelado': 'status-cancelado'
    };
    return classes[status] || 'status-pendente';
}

function getStatusText(status) {
    const textos = {
        'pendente': '⏳ Pendente',
        'confirmado': '✅ Confirmado',
        'concluido': '✓ Concluído',
        'cancelado': '❌ Cancelado'
    };
    return textos[status] || status;
}

async function atualizarStatus(agendamentoId, novoStatus) {
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/barbearia/agendamentos/${agendamentoId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}`
            },
            body: JSON.stringify({ status: novoStatus })
        });
        
        if (!response.ok) throw new Error('Erro ao atualizar status');
        
        mostrarMensagem(`Agendamento ${novoStatus} com sucesso!`);
        
        // Recarregar listas
        await carregarAgendamentosHoje();
        await carregarUltimosAgendamentos();
        
        // Atualizar contadores
        const stats = await fetch('/api/barbearia/dashboard', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        const statsData = await stats.json();
        document.getElementById('agendamentos-pendentes').textContent = statsData.agendamentos_pendentes || 0;
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Verificar autenticação ao carregar
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('elbigdom_token');
    const tipo = localStorage.getItem('elbigdom_tipo');
    
    if (!token || tipo !== 'barbearia') {
        window.location.href = '/login-barbearia';
        return;
    }
    
    // Configurar menu do usuário
    const userMenu = document.getElementById('user-menu');
    const user = JSON.parse(localStorage.getItem('elbigdom_user') || '{}');
    
    userMenu.innerHTML = `
        <div class="dropdown">
            <button class="btn-outline">👤 ${user.nome?.split(' ')[0] || 'Barbearia'}</button>
            <div class="dropdown-content">
                <a href="#" onclick="logout()">Sair</a>
            </div>
        </div>
    `;
    
    await carregarDashboard();
});

function logout() {
    localStorage.removeItem('elbigdom_token');
    localStorage.removeItem('elbigdom_user');
    localStorage.removeItem('elbigdom_tipo');
    window.location.href = '/login-barbearia';
}