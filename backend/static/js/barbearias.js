//busca as barbearias na home
async function carregarBarbearias() {
    const container = document.getElementById('barbearias-grid');
    if (!container) return;
    
    mostrarLoading(true);
    
    try {
        const barbearias = await API.listarBarbearias();
        
        if (barbearias.length === 0) {
            container.innerHTML = '<p style="text-align: center;">Nenhuma barbearia cadastrada ainda.</p>';
            return;
        }
        
        container.innerHTML = barbearias.slice(0, 6).map(barbearia => `
            <div class="barbearia-card">
                <div class="barbearia-image">
                    <img src="${barbearia.logo_url || 'assets/img/placeholder.jpg'}" alt="${barbearia.nome}">
                </div>
                <div class="barbearia-info">
                    <h3 class="barbearia-nome">${barbearia.nome}</h3>
                    <p class="barbearia-endereco">📍 ${barbearia.endereco}</p>
                    <p class="barbearia-endereco">📞 ${formatarTelefone(barbearia.telefone)}</p>
                    <a href="barbearia-detalhe?id=${barbearia.id_barbearia}" class="btn-primary" style="margin-top: 12px; display: inline-block;">Ver Serviços</a>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = '<p style="text-align: center; color: var(--danger);">Erro ao carregar barbearias. Tente novamente.</p>';
        console.error(error);
    } finally {
        mostrarLoading(false);
    }
}