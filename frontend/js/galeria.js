async function compartilharMidia(id) {
    const url = `${window.location.origin}/galeria.html?id=${id}`;
    
    if (navigator.share) {
        try {
            await navigator.share({
                title: 'El Bigodom - Galeria',
                url: url
            });
        } catch (error) {
            console.log('Compartilhamento cancelado');
        }
    } else {
        // Fallback: copiar para clipboard
        navigator.clipboard.writeText(url);
        mostrarMensagem('Link copiado para a área de transferência!');
    }
}