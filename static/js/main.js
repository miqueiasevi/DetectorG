const LIMITE_DIARIO = 3;
const hoje = new Date().toLocaleDateString();
let dados = JSON.parse(localStorage.getItem("detectorg")) || {};

// ================= LOGIN =================

function verificarLogin() {
    const usuario = localStorage.getItem("detectorG_usuario");
    if (!usuario) {
        window.location.href = "login.html";
        return;
    }

    if (!dados[usuario]) {
        dados[usuario] = {
            data: hoje,
            usos: 0,
            pro: false
        };
    }

    verificarStatusServidor();
    atualizarContador();
}

function fazerLogin() {
    const email = document.getElementById("emailLogin").value.trim();
    if (!email) {
        alert("Digite seu e-mail");
        return;
    }
    localStorage.setItem("detectorG_usuario", email);
    window.location.href = "index.html";
}

function logout() {
    localStorage.removeItem("detectorG_usuario");
    window.location.href = "login.html";
}

// ================= RESET DIÁRIO =================

function resetDiario(usuario) {
    if (dados[usuario].data !== hoje) {
        dados[usuario].data = hoje;
        dados[usuario].usos = 0;
        salvar();
    }
}

// ================= VERIFICAR LINK =================

function verificarLink() {
    const usuario = localStorage.getItem("detectorG_usuario");
    resetDiario(usuario);

    if (!dados[usuario].pro && dados[usuario].usos >= LIMITE_DIARIO) {
        alert("Limite diário atingido.");
        return;
    }

    const link = document.getElementById("link").value.trim();
    if (!link) {
        alert("Digite um link.");
        return;
    }

    alert("Link analisado com sucesso!");

    if (!dados[usuario].pro) {
        dados[usuario].usos++;
        salvar();
    }

    atualizarContador();
}

// ================= ATIVAR PRO =================

function ativarPRO() {
    const usuario = localStorage.getItem("detectorG_usuario");
    const codigo = document.getElementById("codigoPRO").value.trim();

    fetch("/ativar_pro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            codigo: codigo,
            email: usuario
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "ok") {
            alert("PRO ativado até " + data.expira_em);
            verificarStatusServidor();
        } else {
            alert(data.mensagem);
        }
    });
}

// ================= STATUS SERVIDOR =================

function verificarStatusServidor() {
    const usuario = localStorage.getItem("detectorG_usuario");

    fetch("/status_pro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: usuario })
    })
    .then(res => res.json())
    .then(data => {
        dados[usuario].pro = data.pro;
        salvar();
        atualizarContador();
    });
}

// ================= CONTADOR =================

function atualizarContador() {
    const usuario = localStorage.getItem("detectorG_usuario");
    const contador = document.getElementById("contador");

    if (dados[usuario].pro) {
        contador.textContent = "Plano PRO ativo (ilimitado)";
    } else {
        contador.textContent = 
            "Uso gratuito: " + dados[usuario].usos + "/" + LIMITE_DIARIO;
    }
}

// ================= SALVAR =================

function salvar() {
    localStorage.setItem("detectorg", JSON.stringify(dados));
}

window.onload = verificarLogin;
