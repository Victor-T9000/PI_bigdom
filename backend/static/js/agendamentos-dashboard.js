let agendamentosAtuais = [];
let filtrosAtuais = {};

// Carregar barbeiros para o filtro
async function carregarBarbeirosFiltro() {
    try {
        const response = await fetch('/api/barbearia/barbeiros', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        const barbeiros = await response.json();
        const select = document.getElementById('filtro-barbeiro');
        
        select.innerHTML = '<option value="">Todos</option>' + 
            barbeiros.map(b => `<option value="${b.id_barbeiro}">${b.nome}</option>`).join('');
        
    } catch (error) {
        console.error('Erro ao carregar barbeiros:', error);
    }
}

// Carregar agendamentos
async function carregarAgendamentos() {
    mostrarLoading(true);
    
    try {
        let url = '/api/barbearia/agendamentos';
        const params = new URLSearchParams();
        
        if (filtrosAtuais.status) params.append('status', filtrosAtuais.status);
        if (filtrosAtuais.data) params.append('data', filtrosAtuais.data);
        if (filtrosAtuais.barbeiro_id) params.append('barbeiro_id', filtrosAtuais.barbeiro_id);
        
        if (params.toString()) url += `?${params.toString()}`;
        
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        agendamentosAtuais = await response.json();
        
        atualizarResumo();
        renderizarAgendamentos();
        
    } catch (error) {
        document.getElementById('agendamentos-container').innerHTML = 
            '<div class="empty-state"><div class="emoji">❌</div><p>Erro ao carregar agendamentos</p></div>';
    } finally {
        mostrarLoading(false);
    }
}

// Atualizar resumo de estatísticas
function atualizarResumo() {
    const pendentes = agendamentosAtuais.filter(a => a.status === 'pendente').length;
    const confirmados = agendamentosAtuais.filter(a => a.status === 'confirmado').length;
    const concluidos = agendamentosAtuais.filter(a => a.status === 'concluido').length;
    const cancelados = agendamentosAtuais.filter(a => a.status === 'cancelado').length;
    
    document.getElementById('total-pendente').textContent = pendentes;
    document.getElementById('total-confirmado').textContent = confirmados;
    document.getElementById('total-concluido').textContent = concluidos;
    document.getElementById('total-cancelado').textContent = cancelados;
}

// Renderizar lista de agendamentos
function renderizarAgendamentos() {
    const container = document.getElementById('agendamentos-container');
    
    if (agendamentosAtuais.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="emoji">📭</div>
                <p>Nenhum agendamento encontrado</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = agendamentosAtuais.map(ag => `
        <div class="agendamento-card" data-id="${ag.id_agendamento}">
            <div class="agendamento-card-header">
                <div class="cliente-info">
                    <strong>${ag.cliente_nome || 'Cliente'}</strong>
                    <span class="agendamento-status status-${ag.status}">${getStatusText(ag.status)}</span>
                </div>
                <div class="agendamento-card-actions">
                    <button class="btn-icon" onclick="verDetalhes(${ag.id_agendamento})" title="Detalhes">👁️</button>
                    ${ag.status === 'pendente' ? `
                        <button class="btn-icon btn-success-icon" onclick="atualizarStatus(${ag.id_agendamento}, 'confirmado')" title="Confirmar">✅</button>
                        <button class="btn-icon btn-danger-icon" onclick="atualizarStatus(${ag.id_agendamento}, 'cancelado')" title="Cancelar">❌</button>
                    ` : ''}
                    ${ag.status === 'confirmado' ? `
                        <button class="btn-icon btn-success-icon" onclick="atualizarStatus(${ag.id_agendamento}, 'concluido')" title="Concluir">✓</button>
                    ` : ''}
                </div>
            </div>
            <div class="agendamento-card-body">
                <div class="detalhes-grid">
                    <div class="detalhe-item">
                        <span class="label">📅 Data:</span>
                        <span>${formatarDataHora(ag.data_agendamento)}</span>
                    </div>
                    <div class="detalhe-item">
                        <span class="label">✂️ Serviço:</span>
                        <span>${ag.servico_nome || '-'}</span>
                    </div>
                    <div class="detalhe-item">
                        <span class="label">💈 Barbeiro:</span>
                        <span>${ag.barbeiro_nome || '-'}</span>
                    </div>
                    <div class="detalhe-item">
                        <span class="label">💰 Valor:</span>
                        <span>${formatarMoeda(ag.preco || 0)}</span>
                    </div>
                    <div class="detalhe-item">
                        <span class="label">📞 Telefone:</span>
                        <span>${formatarTelefone(ag.cliente_telefone || '')}</span>
                    </div>
                    <div class="detalhe-item">
                        <span class="label">📧 Email:</span>
                        <span>${ag.cliente_email || '-'}</span>
                    </div>
                </div>
                ${ag.observacao ? `
                    <div class="observacao">
                        <span class="label">📝 Observação:</span>
                        <p>${ag.observacao}</p>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Ver detalhes do agendamento
function verDetalhes(id) {
    const ag = agendamentosAtuais.find(a => a.id_agendamento === id);
    if (!ag) return;
    
    const modalBody = document.getElementById('detalhes-content');
    modalBody.innerHTML = `
        <div class="detalhes-agendamento">
            <div class="detalhe-linha">
                <strong>Cliente:</strong> ${ag.cliente_nome || 'Cliente'}
            </div>
            <div class="detalhe-linha">
                <strong>Telefone:</strong> ${formatarTelefone(ag.cliente_telefone || '')}
            </div>
            <div class="detalhe-linha">
                <strong>Email:</strong> ${ag.cliente_email || '-'}
            </div>
            <hr>
            <div class="detalhe-linha">
                <strong>Data:</strong> ${formatarDataHora(ag.data_agendamento)}
            </div>
            <div class="detalhe-linha">
                <strong>Serviço:</strong> ${ag.servico_nome || '-'}
            </div>
            <div class="detalhe-linha">
                <strong>Barbeiro:</strong> ${ag.barbeiro_nome || '-'}
            </div>
            <div class="detalhe-linha">
                <strong>Valor:</strong> ${formatarMoeda(ag.preco || 0)}
            </div>
            <div class="detalhe-linha">
                <strong>Status:</strong> <span class="status-${ag.status}">${getStatusText(ag.status)}</span>
            </div>
            ${ag.observacao ? `
                <hr>
                <div class="detalhe-linha">
                    <strong>Observação:</strong>
                    <p style="margin-top: 8px;">${ag.observacao}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    document.getElementById('modal-detalhes').classList.add('active');
}

function fecharModalDetalhes() {
    document.getElementById('modal-detalhes').classList.remove('active');
}

// Atualizar status do agendamento
async function atualizarStatus(id, novoStatus) {
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/barbearia/agendamentos/${id}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}`
            },
            body: JSON.stringify({ status: novoStatus })
        });
        
        if (!response.ok) throw new Error('Erro ao atualizar status');
        
        mostrarMensagem(`Agendamento ${getStatusText(novoStatus).toLowerCase()}!`);
        await carregarAgendamentos();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Aplicar filtros
function aplicarFiltros() {
    filtrosAtuais = {
        status: document.getElementById('filtro-status').value,
        data: document.getElementById('filtro-data').value,
        barbeiro_id: document.getElementById('filtro-barbeiro').value
    };
    
    carregarAgendamentos();
}

// Limpar filtros
function limparFiltros() {
    document.getElementById('filtro-status').value = '';
    document.getElementById('filtro-data').value = '';
    document.getElementById('filtro-barbeiro').value = '';
    filtrosAtuais = {};
    carregarAgendamentos();
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

// Verificar autenticação
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
    
    await carregarBarbeirosFiltro();
    await carregarAgendamentos();
});

function logout() {
    localStorage.removeItem('elbigdom_token');
    localStorage.removeItem('elbigdom_user');
    localStorage.removeItem('elbigdom_tipo');
    window.location.href = '/login-barbearia';
}