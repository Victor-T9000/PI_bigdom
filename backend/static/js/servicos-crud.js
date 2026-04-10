let servicoParaDeletar = null;

// Carregar lista de serviços
async function carregarServicos() {
    const container = document.getElementById('servicos-grid');
    
    try {
        const response = await fetch('/api/barbearia/servicos', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        const servicos = await response.json();
        
        if (servicos.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="emoji">💈</div>
                    <p>Nenhum serviço cadastrado ainda</p>
                    <button class="btn-primary" onclick="abrirModalCadastro()">Cadastrar Primeiro Serviço</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = servicos.map(servico => `
            <div class="servico-card">
                <div class="servico-header">
                    <h3>${servico.nome}</h3>
                    <div class="servico-actions">
                        <button class="btn-icon" onclick="editarServico(${servico.id_servico})" title="Editar">✏️</button>
                        <button class="btn-icon" onclick="abrirModalDelete(${servico.id_servico}, '${servico.nome}')" title="Remover">🗑️</button>
                    </div>
                </div>
                ${servico.descricao ? `<p class="servico-descricao">${servico.descricao}</p>` : ''}
                <div class="servico-info">
                    <span class="servico-preco">${formatarMoeda(servico.preco)}</span>
                    <span class="servico-duracao">⏱️ ${servico.duracao_minutos} min</span>
                    ${servico.categoria ? `<span class="servico-categoria">📁 ${servico.categoria}</span>` : ''}
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = '<div class="empty-state" style="grid-column: 1/-1;"><p style="color: var(--danger);">Erro ao carregar serviços</p></div>';
    }
}

// Abrir modal de cadastro
function abrirModalCadastro() {
    document.getElementById('modal-title').textContent = 'Novo Serviço';
    document.getElementById('servico-id').value = '';
    document.getElementById('nome').value = '';
    document.getElementById('descricao').value = '';
    document.getElementById('preco').value = '';
    document.getElementById('duracao').value = '30';
    document.getElementById('categoria').value = '';
    document.getElementById('modal-servico').classList.add('active');
}

// Editar serviço
async function editarServico(id) {
    mostrarLoading(true);
    
    try {
        const response = await fetch('/api/barbearia/servicos', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        const servicos = await response.json();
        const servico = servicos.find(s => s.id_servico === id);
        
        if (servico) {
            document.getElementById('modal-title').textContent = 'Editar Serviço';
            document.getElementById('servico-id').value = servico.id_servico;
            document.getElementById('nome').value = servico.nome;
            document.getElementById('descricao').value = servico.descricao || '';
            document.getElementById('preco').value = servico.preco;
            document.getElementById('duracao').value = servico.duracao_minutos;
            document.getElementById('categoria').value = servico.categoria || '';
            document.getElementById('modal-servico').classList.add('active');
        }
    } catch (error) {
        mostrarMensagem('Erro ao carregar dados do serviço', 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Formatar preço no input
function formatarPrecoInput(valor) {
    let v = valor.replace(/\D/g, '');
    v = (parseInt(v) / 100).toFixed(2);
    v = v.replace('.', ',');
    v = v.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return 'R$ ' + v;
}

// Salvar serviço (criar ou atualizar)
async function salvarServico() {
    const id = document.getElementById('servico-id').value;
    let preco = document.getElementById('preco').value;
    preco = preco.replace('R$', '').replace(/\./g, '').replace(',', '.').trim();
    
    const dados = {
        nome: document.getElementById('nome').value,
        descricao: document.getElementById('descricao').value,
        preco: parseFloat(preco),
        duracao_minutos: parseInt(document.getElementById('duracao').value),
        categoria: document.getElementById('categoria').value
    };
    
    if (!dados.nome || !dados.preco) {
        mostrarMensagem('Preencha nome e preço do serviço', 'error');
        return;
    }
    
    mostrarLoading(true);
    
    try {
        const url = id ? `/api/barbearia/servicos/${id}` : '/api/barbearia/servicos';
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}`
            },
            body: JSON.stringify(dados)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao salvar');
        }
        
        mostrarMensagem(id ? 'Serviço atualizado!' : 'Serviço cadastrado!');
        fecharModal();
        carregarServicos();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Abrir modal de exclusão
function abrirModalDelete(id, nome) {
    servicoParaDeletar = id;
    document.getElementById('delete-nome').textContent = nome;
    document.getElementById('modal-delete').classList.add('active');
}

// Confirmar exclusão
async function confirmarDelete() {
    if (!servicoParaDeletar) return;
    
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/barbearia/servicos/${servicoParaDeletar}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        if (!response.ok) throw new Error('Erro ao remover');
        
        mostrarMensagem('Serviço removido com sucesso');
        fecharModalDelete();
        carregarServicos();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

function fecharModal() {
    document.getElementById('modal-servico').classList.remove('active');
}

function fecharModalDelete() {
    document.getElementById('modal-delete').classList.remove('active');
    servicoParaDeletar = null;
}

// Máscara de preço
document.getElementById('preco')?.addEventListener('input', function(e) {
    let valor = e.target.value;
    if (valor.includes('R$')) {
        valor = valor.replace('R$', '');
    }
    e.target.value = 'R$ ' + valor;
});

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
    
    carregarServicos();
});

function logout() {
    localStorage.removeItem('elbigdom_token');
    localStorage.removeItem('elbigdom_user');
    localStorage.removeItem('elbigdom_tipo');
    window.location.href = '/login-barbearia';
}