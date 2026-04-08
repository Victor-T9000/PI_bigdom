const API = {
    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...getAuthHeaders(),
            ...options.headers
        };
        
        const config = {
            ...options,
            headers
        };
        
        try {
            const response = await fetch(`${CONFIG.API_URL}${endpoint}`, config);
            
            if (response.status === 401) {
                logout();
                throw new Error('Sessão expirada. Faça login novamente.');
            }
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            console.error(`Erro na API (${endpoint}):`, error);
            throw error;
        }
    },
    
    //  AUTENTICAÇÃOO
    async login(email, senha) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, senha })
        });
        
        if (data.token) {
            salvarToken(data.token, data.usuario);
        }
        return data;
    },
    
    async registrar(usuario) {
        return this.request('/auth/registrar', {
            method: 'POST',
            body: JSON.stringify(usuario)
        });
    },
    
    // ========== BARBEARIAS ==========
    async listarBarbearias(filtros = {}) {
        const params = new URLSearchParams(filtros).toString();
        return this.request(`/barbearias${params ? `?${params}` : ''}`);
    },
    
    async getBarbearia(id) {
        return this.request(`/barbearias/${id}`);
    },
    
    // ========== BARBEIROS ==========
    async listarBarbeiros(filtros = {}) {
        const params = new URLSearchParams(filtros).toString();
        return this.request(`/barbeiros${params ? `?${params}` : ''}`);
    },
    
    async getBarbeiro(id) {
        return this.request(`/barbeiros/${id}`);
    },
    
    async getHorariosBarbeiro(barbeiroId, data) {
        return this.request(`/barbeiros/${barbeiroId}/horarios?data=${data}`);
    },
    
    // ========== SERVIÇOS ==========
    async listarServicos(filtros = {}) {
        const params = new URLSearchParams(filtros).toString();
        return this.request(`/servicos${params ? `?${params}` : ''}`);
    },
    
    // ========== AGENDAMENTOS ==========
    async criarAgendamento(agendamento) {
        return this.request('/agendamentos', {
            method: 'POST',
            body: JSON.stringify(agendamento)
        });
    },
    
    async meusAgendamentos() {
        return this.request('/agendamentos/meus');
    },
    
    async cancelarAgendamento(id) {
        return this.request(`/agendamentos/${id}`, {
            method: 'DELETE'
        });
    },
    
    // ========== AVALIAÇÕES ==========
    async criarAvaliacao(avaliacao) {
        return this.request('/avaliacoes', {
            method: 'POST',
            body: JSON.stringify(avaliacao)
        });
    },
    
    async getAvaliacoesBarbeiro(barbeiroId) {
        return this.request(`/avaliacoes/barbeiro/${barbeiroId}`);
    },
    
    // ========== CUPONS ==========
    async meusCupons() {
        return this.request('/cupons/meus');
    },
    
    // ========== GALERIA ==========
    async listarGaleria(filtros = {}) {
        const params = new URLSearchParams(filtros).toString();
        return this.request(`/galeria${params ? `?${params}` : ''}`);
    }
};