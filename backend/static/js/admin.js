let meuChart = null;

// Carregar estatísticas
async function carregarEstatisticas() {
    try {
        const response = await fetch('/api/admin/estatisticas', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        const stats = await response.json();
        
        document.getElementById('total-barbearias').textContent = stats.total_barbearias || 0;
        document.getElementById('total-barbeiros').textContent = stats.total_barbeiros || 0;
        document.getElementById('total-clientes').textContent = stats.total_clientes || 0;
        document.getElementById('total-agendamentos').textContent = stats.total_agendamentos || 0;
        document.getElementById('pendentes').textContent = stats.pendentes || 0;
        
        // Criar gráfico
        if (stats.agendamentos_mensal && document.getElementById('grafico-agendamentos')) {
            const meses = stats.agendamentos_mensal.map(m => m.mes).reverse();
            const totais = stats.agendamentos_mensal.map(m => m.total).reverse();
            
            if (meuChart) meuChart.destroy();
            
            const ctx = document.getElementById('grafico-agendamentos').getContext('2d');
            meuChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: meses,
                    datasets: [{
                        label: 'Agendamentos',
                        data: totais,
                        borderColor: '#FFD700',
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true
                }
            });
        }
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Carregar barbearias pendentes
async function carregarPendentes() {
    const container = document.getElementById('pendentes-container');
    if (!container) return;
    
    mostrarLoading(true);
    
    try {
        const response = await fetch('/api/admin/barbearias/pendentes', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        const barbearias = await response.json();
        
        if (barbearias.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="emoji">✅</div>
                    <p>Nenhuma barbearia aguardando aprovação</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = barbearias.map(b => `
            <div class="card pending-card" data-id="${b.id_barbearia}">
                <div class="pending-header">
                    <div class="pending-icon">🏪</div>
                    <div class="pending-info">
                        <h3>${b.nome}</h3>
                        <p>📧 ${b.email}</p>
                        <p>📞 ${formatarTelefone(b.telefone)}</p>
                        <p>📍 ${b.endereco}, ${b.cidade}/${b.estado}</p>
                        ${b.descricao ? `<p>📝 ${b.descricao}</p>` : ''}
                        <p class="data-cadastro">📅 Cadastrado em ${formatarData(b.data_cadastro)}</p>
                    </div>
                </div>
                <div class="pending-actions">
                    <button class="btn-success" onclick="aprovarBarbearia(${b.id_barbearia})">✓ Aprovar</button>
                    <button class="btn-danger" onclick="rejeitarBarbearia(${b.id_barbearia})">✗ Rejeitar</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><p>Erro ao carregar barbearias pendentes</p></div>';
    } finally {
        mostrarLoading(false);
    }
}

// Aprovar barbearia
async function aprovarBarbearia(id) {
    if (!confirm('Aprovar esta barbearia?')) return;
    
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/admin/barbearias/aprovar/${id}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        if (!response.ok) throw new Error('Erro ao aprovar');
        
        mostrarMensagem('Barbearia aprovada com sucesso!');
        carregarPendentes();
        
        if (document.getElementById('total-barbearias')) {
            carregarEstatisticas();
        }
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Rejeitar barbearia
async function rejeitarBarbearia(id) {
    if (!confirm('Tem certeza que deseja rejeitar esta barbearia? Esta ação não pode ser desfeita.')) return;
    
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/admin/barbearias/rejeitar/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        if (!response.ok) throw new Error('Erro ao rejeitar');
        
        mostrarMensagem('Barbearia rejeitada e removida');
        carregarPendentes();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Verificar autenticação
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('elbigdom_token');
    const tipo = localStorage.getItem('elbigdom_tipo');
    
    if (!token || tipo !== 'admin') {
        window.location.href = '/login-admin';
        return;
    }
    
    // Configurar menu do usuário
    const userMenu = document.getElementById('user-menu');
    if (userMenu) {
        const user = JSON.parse(localStorage.getItem('elbigdom_user') || '{}');
        userMenu.innerHTML = `
            <div class="dropdown">
                <button class="btn-outline">👑 ${user.nome || 'Admin'}</button>
                <div class="dropdown-content">
                    <a href="#" onclick="logout()">Sair</a>
                </div>
            </div>
        `;
    }
    
    // Carregar dados específicos da página
    if (window.location.pathname.includes('/admin/dashboard')) {
        carregarEstatisticas();
    } else if (window.location.pathname.includes('/admin/pendentes')) {
        carregarPendentes();
    }
});

function logout() {
    localStorage.removeItem('elbigdom_token');
    localStorage.removeItem('elbigdom_user');
    localStorage.removeItem('elbigdom_tipo');
    window.location.href = '/login-admin';
}