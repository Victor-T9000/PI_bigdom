let barbeiroParaDeletar = null;

// Carregar lista de barbeiros
async function carregarBarbeiros() {
    const tbody = document.getElementById('barbeiros-tbody');
    
    try {
        const response = await fetch('/api/barbearia/barbeiros', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        const barbeiros = await response.json();
        
        if (barbeiros.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Nenhum barbeiro cadastrado</td></tr>';
            return;
        }
        
        tbody.innerHTML = barbeiros.map(barbeiro => `
            <tr>
                <td>
                    ${barbeiro.foto_url ? `<img src="${barbeiro.foto_url}" class="avatar-small">` : '👤'}
                    <strong>${barbeiro.nome}</strong>
                </td>
                <td>${barbeiro.email}</td>
                <td>${formatarTelefone(barbeiro.telefone)}</td>
                <td>${barbeiro.especialidade || '-'}</td>
                <td>${barbeiro.total_atendimentos || 0}</td>
                <td>${getEstrelas(barbeiro.avaliacao_media || 0)} (${barbeiro.total_avaliacoes || 0})</td>
                <td class="actions">
                    <button class="btn-icon" onclick="editarBarbeiro(${barbeiro.id_barbeiro})" title="Editar">✏️</button>
                    <button class="btn-icon" onclick="abrirModalDelete(${barbeiro.id_barbeiro}, '${barbeiro.nome}')" title="Remover">🗑️</button>
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--danger);">Erro ao carregar barbeiros</td></tr>';
    }
}

// Abrir modal de cadastro
function abrirModalCadastro() {
    document.getElementById('modal-title').textContent = 'Novo Barbeiro';
    document.getElementById('barbeiro-id').value = '';
    document.getElementById('nome').value = '';
    document.getElementById('email').value = '';
    document.getElementById('telefone').value = '';
    document.getElementById('especialidade').value = '';
    document.getElementById('foto_url').value = '';
    document.getElementById('modal-barbeiro').classList.add('active');
}

// Editar barbeiro
async function editarBarbeiro(id) {
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/barbearia/barbeiros`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        const barbeiros = await response.json();
        const barbeiro = barbeiros.find(b => b.id_barbeiro === id);
        
        if (barbeiro) {
            document.getElementById('modal-title').textContent = 'Editar Barbeiro';
            document.getElementById('barbeiro-id').value = barbeiro.id_barbeiro;
            document.getElementById('nome').value = barbeiro.nome;
            document.getElementById('email').value = barbeiro.email;
            document.getElementById('telefone').value = barbeiro.telefone;
            document.getElementById('especialidade').value = barbeiro.especialidade || '';
            document.getElementById('foto_url').value = barbeiro.foto_url || '';
            document.getElementById('modal-barbeiro').classList.add('active');
        }
    } catch (error) {
        mostrarMensagem('Erro ao carregar dados do barbeiro', 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Salvar barbeiro (criar ou atualizar)
async function salvarBarbeiro() {
    const id = document.getElementById('barbeiro-id').value;
    const dados = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        telefone: document.getElementById('telefone').value,
        especialidade: document.getElementById('especialidade').value,
        foto_url: document.getElementById('foto_url').value
    };
    
    if (!dados.nome || !dados.email || !dados.telefone) {
        mostrarMensagem('Preencha todos os campos obrigatórios', 'error');
        return;
    }
    
    mostrarLoading(true);
    
    try {
        const url = id ? `/api/barbearia/barbeiros/${id}` : '/api/barbearia/barbeiros';
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
        
        mostrarMensagem(id ? 'Barbeiro atualizado!' : 'Barbeiro cadastrado!');
        fecharModal();
        carregarBarbeiros();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Abrir modal de exclusão
function abrirModalDelete(id, nome) {
    barbeiroParaDeletar = id;
    document.getElementById('delete-nome').textContent = nome;
    document.getElementById('modal-delete').classList.add('active');
}

// Confirmar exclusão
async function confirmarDelete() {
    if (!barbeiroParaDeletar) return;
    
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/barbearia/barbeiros/${barbeiroParaDeletar}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        if (!response.ok) throw new Error('Erro ao remover');
        
        mostrarMensagem('Barbeiro removido com sucesso');
        fecharModalDelete();
        carregarBarbeiros();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

function fecharModal() {
    document.getElementById('modal-barbeiro').classList.remove('active');
}

function fecharModalDelete() {
    document.getElementById('modal-delete').classList.remove('active');
    barbeiroParaDeletar = null;
}

// Máscara de telefone
document.getElementById('telefone')?.addEventListener('input', function(e) {
    let valor = e.target.value.replace(/\D/g, '');
    if (valor.length <= 11) {
        valor = valor.replace(/(\d{2})(\d)/, '($1) $2');
        valor = valor.replace(/(\d{5})(\d)/, '$1-$2');
        e.target.value = valor;
    }
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
    
    carregarBarbeiros();
});

function logout() {
    localStorage.removeItem('elbigdom_token');
    localStorage.removeItem('elbigdom_user');
    localStorage.removeItem('elbigdom_tipo');
    window.location.href = '/login-barbearia';
}