let especialistaSelecionado = null;

// Carrega histórico na inicialização
fetch('/api/load_history')
    .then(response => response.json())
    .then(data => {
        data.forEach(mensagem => {
            adicionarMensagem(mensagem.pergunta, true);
            adicionarMensagem(mensagem.resposta, false);
        });
    });

document.getElementById('form-chat').addEventListener('submit', function (e) {
    e.preventDefault();
    const input = document.getElementById('mensagem');
    const texto = input.value;
    if (!texto || !especialistaSelecionado) {
        alert("Digite uma mensagem e selecione um especialista.");
        return;
    }

    adicionarMensagem(texto, true);

    fetch('/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: texto, especialista_id: especialistaSelecionado })
    })
    .then(response => response.json())
    .then(data => {
        adicionarMensagem(data.response, false);
    });

    input.value = '';
});

function adicionarMensagem(texto, usuario) {
    const chat = document.getElementById('chat');
    const mensagem = document.createElement('div');
    mensagem.className = usuario ? 'text-end mb-2 w-75 ms-auto' : 'text-start mb-2 w-75 me-auto';
    mensagem.innerHTML = `<span class="alert text-break d-block alert-${usuario ? 'primary' : 'secondary'}">${texto}</span>`;
    chat.appendChild(mensagem);
    chat.scrollTop = chat.scrollHeight;
}

function selecionarEspecialista(id) {
    especialistaSelecionado = id;
    alert('Especialista selecionado!');
}