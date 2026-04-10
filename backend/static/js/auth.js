function salvarToken(token, usuario) {
    localStorage.setItem(CONFIG.TOKEN_KEY, token);
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(usuario));
}

function getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
}

function getUsuario() {
    const user = localStorage.getItem(CONFIG.USER_KEY);
    return user ? JSON.parse(user) : null;
}

function isAutenticado() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
    window.location.href = 'login';
}

function getAuthHeaders() {
    const token = getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function verificarAutenticacao(redirectIfNot = true) {
    if (!isAutenticado() && redirectIfNot) {
        window.location.href = 'login';
        return false;
    }
    return true;
}

function atualizarMenuUsuario() {
    const userMenu = document.getElementById('user-menu');
    if (!userMenu) return;
    
    if (isAutenticado()) {
        const usuario = getUsuario();
        userMenu.innerHTML = `
            <div class="dropdown" style="position: relative;">
                <button class="btn-outline" style="display: flex; align-items: center; gap: 8px;">
                    👤 ${usuario.nome.split(' ')[0]}
                </button>
                <div class="dropdown-content" style="position: absolute; right: 0; top: 100%; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); min-width: 180px; display: none; z-index: 100;">
                    <a href="perfil.html" style="display: block; padding: 10px 16px; color: #333; text-decoration: none;">Meu Perfil</a>
                    <a href="meus-agendamentos" style="display: block; padding: 10px 16px; color: #333; text-decoration: none;">Meus Agendamentos</a>
                    <a href="cupons.html" style="display: block; padding: 10px 16px; color: #333; text-decoration: none;">Meus Cupons</a>
                    <hr style="margin: 8px 0;">
                    <a href="#" onclick="logout()" style="display: block; padding: 10px 16px; color: #FF3B30; text-decoration: none;">Sair</a>
                </div>
            </div>
        `;
        
        // Adicionar evento de hover
        const dropdown = userMenu.querySelector('.dropdown');
        const content = dropdown.querySelector('.dropdown-content');
        dropdown.addEventListener('mouseenter', () => content.style.display = 'block');
        dropdown.addEventListener('mouseleave', () => content.style.display = 'none');
    } else {
        userMenu.innerHTML = `
            <a href="login.html" class="btn-outline">Entrar</a>
            <a href="cadastro.html" class="btn-primary">Cadastrar</a>
        `;
    }
}