let barbeiroAtual = null;
let barbeirosLista = [];
let horarioEditando = null;

// Nomes dos dias da semana
const diasNomes = {
    1: 'Segunda-feira',
    2: 'Terça-feira',
    3: 'Quarta-feira',
    4: 'Quinta-feira',
    5: 'Sexta-feira',
    6: 'Sábado',
    7: 'Domingo'
};

// Carregar lista de barbeiros
async function carregarBarbeiros() {
    const select = document.getElementById('selecionar-barbeiro');
    
    try {
        const response = await fetch('/api/barbearia/barbeiros', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        barbeirosLista = await response.json();
        
        if (barbeirosLista.length === 0) {
            select.innerHTML = '<option value="">Nenhum barbeiro cadastrado</option>';
            return;
        }
        
        select.innerHTML = '<option value="">Selecione um barbeiro...</option>' + 
            barbeirosLista.map(b => `<option value="${b.id_barbeiro}">${b.nome}</option>`).join('');
        
    } catch (error) {
        select.innerHTML = '<option value="">Erro ao carregar barbeiros</option>';
    }
}

// Carregar horários do barbeiro selecionado
async function carregarHorarios() {
    const select = document.getElementById('selecionar-barbeiro');
    const barbeiroId = select.value;
    
    if (!barbeiroId) {
        document.getElementById('horarios-section').style.display = 'none';
        return;
    }
    
    barbeiroAtual = barbeirosLista.find(b => b.id_barbeiro == barbeiroId);
    document.getElementById('barbeiro-nome').textContent = `Horários de ${barbeiroAtual?.nome}`;
    document.getElementById('horarios-section').style.display = 'block';
    
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/barbearia/barbeiros/${barbeiroId}/horarios`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        const horarios = await response.json();
        
        // Limpar todos os dias
        for (let i = 1; i <= 7; i++) {
            document.getElementById(`horarios-${i}`).innerHTML = '';
        }
        
        // Distribuir horários por dia
        horarios.forEach(horario => {
            const container = document.getElementById(`horarios-${horario.dia_semana}`);
            if (container) {
                container.innerHTML += `
                    <div class="horario-item" data-id="${horario.id_horario}">
                        <span>${horario.hora_inicio.substring(0,5)} - ${horario.hora_fim.substring(0,5)}</span>
                        <div class="horario-actions">
                            <button class="btn-icon" onclick="editarHorario(${horario.id_horario}, ${horario.dia_semana}, '${horario.hora_inicio}', '${horario.hora_fim}')" title="Editar">✏️</button>
                            <button class="btn-icon" onclick="removerHorario(${horario.id_horario})" title="Remover">🗑️</button>
                        </div>
                    </div>
                `;
            }
        });
        
        // Mostrar mensagem para dias sem horário
        for (let i = 1; i <= 7; i++) {
            const container = document.getElementById(`horarios-${i}`);
            if (container && container.innerHTML === '') {
                container.innerHTML = '<div class="sem-horario">Nenhum horário configurado</div>';
            }
        }
        
    } catch (error) {
        mostrarMensagem('Erro ao carregar horários', 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Abrir modal para adicionar horário
function abrirModalHorario(diaSemana = null) {
    if (!barbeiroAtual) {
        mostrarMensagem('Selecione um barbeiro primeiro', 'warning');
        return;
    }
    
    document.getElementById('modal-title').textContent = 'Adicionar Horário';
    document.getElementById('horario-id').value = '';
    document.getElementById('dia-semana').value = diaSemana || '';
    document.getElementById('dia-nome').value = diaSemana ? diasNomes[diaSemana] : '';
    document.getElementById('hora-inicio').value = '09:00';
    document.getElementById('hora-fim').value = '18:00';
    
    if (diaSemana) {
        document.getElementById('modal-horario').classList.add('active');
    } else {
        mostrarMensagem('Selecione um dia da semana', 'warning');
    }
}

// Editar horário
function editarHorario(id, diaSemana, horaInicio, horaFim) {
    horarioEditando = id;
    document.getElementById('modal-title').textContent = 'Editar Horário';
    document.getElementById('horario-id').value = id;
    document.getElementById('dia-semana').value = diaSemana;
    document.getElementById('dia-nome').value = diasNomes[diaSemana];
    document.getElementById('hora-inicio').value = horaInicio.substring(0,5);
    document.getElementById('hora-fim').value = horaFim.substring(0,5);
    document.getElementById('modal-horario').classList.add('active');
}

// Salvar horário
async function salvarHorario() {
    if (!barbeiroAtual) {
        mostrarMensagem('Selecione um barbeiro', 'error');
        return;
    }
    
    const id = document.getElementById('horario-id').value;
    const diaSemana = parseInt(document.getElementById('dia-semana').value);
    const horaInicio = document.getElementById('hora-inicio').value;
    const horaFim = document.getElementById('hora-fim').value;
    
    if (!diaSemana || !horaInicio || !horaFim) {
        mostrarMensagem('Preencha todos os campos', 'error');
        return;
    }
    
    if (horaInicio >= horaFim) {
        mostrarMensagem('Hora início deve ser menor que hora fim', 'error');
        return;
    }
    
    mostrarLoading(true);
    
    try {
        let response;
        
        if (id) {
            // Atualizar (DELETE + INSERT)
            await fetch(`/api/barbearia/horarios/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
            });
            
            response = await fetch(`/api/barbearia/barbeiros/${barbeiroAtual.id_barbeiro}/horarios`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}`
                },
                body: JSON.stringify({ dia_semana: diaSemana, hora_inicio: horaInicio, hora_fim: horaFim })
            });
        } else {
            response = await fetch(`/api/barbearia/barbeiros/${barbeiroAtual.id_barbeiro}/horarios`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}`
                },
                body: JSON.stringify({ dia_semana: diaSemana, hora_inicio: horaInicio, hora_fim: horaFim })
            });
        }
        
        if (!response.ok) throw new Error('Erro ao salvar horário');
        
        mostrarMensagem(id ? 'Horário atualizado!' : 'Horário adicionado!');
        fecharModalHorario();
        carregarHorarios();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Remover horário
async function removerHorario(id) {
    if (!confirm('Tem certeza que deseja remover este horário?')) return;
    
    mostrarLoading(true);
    
    try {
        const response = await fetch(`/api/barbearia/horarios/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('elbigdom_token')}` }
        });
        
        if (!response.ok) throw new Error('Erro ao remover horário');
        
        mostrarMensagem('Horário removido!');
        carregarHorarios();
        
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        mostrarLoading(false);
    }
}

function fecharModalHorario() {
    document.getElementById('modal-horario').classList.remove('active');
    horarioEditando = null;
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
    
    await carregarBarbeiros();
});

function logout() {
    localStorage.removeItem('elbigdom_token');
    localStorage.removeItem('elbigdom_user');
    localStorage.removeItem('elbigdom_tipo');
    window.location.href = '/login-barbearia';
}