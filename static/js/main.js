const LIMITE_DIARIO = 3;
const hoje = new Date().toLocaleDateString();
let dados = JSON.parse(localStorage.getItem("detectorg")) || {};

// ================= LOGIN =================

function verificarLogin() {
    let usuario = localStorage.getItem("usuario");

    if (!usuario) {
        usuario = "user_" + Math.floor(Math.random() * 10000);
        localStorage.setItem("usuario", usuario);
    }

    if (!dados[usuario]) {
        dados[usuario] = {
            data: hoje,
            usos: 0
        };
    }

    verificarStatusServidor();
    atualizarContador();
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

async function verificarLink() {
    const usuario = localStorage.getItem("usuario");
    resetDiario(usuario);

    const link = document.getElementById("link").value.trim();

    if (!link) {
        alert("Digite um link.");
        return;
    }

    const res = await fetch("/verificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ link, usuario })
    });

    const data = await res.json();

    if (data.status === "ok") {

        document.getElementById("resultado").innerHTML =
            `<b>Nível:</b> ${data.resultado.nivel}<br>
             <b>Riscos:</b> ${data.resultado.riscos.join(", ") || "Nenhum"}`;

        if (data.restantes !== undefined) {
            document.getElementById("contador").innerText =
                "Restantes hoje: " + data.restantes;
        }

    } else {
        alert(data.mensagem);
    }
}

// ================= STATUS SERVIDOR =================

async function verificarStatusServidor() {
    const usuario = localStorage.getItem("usuario");

    const res = await fetch("/status_pro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario })
    });

    const data = await res.json();

    dados[usuario].pro = data.pro;
    salvar();
    atualizarContador();
}

// ================= CONTADOR =================

function atualizarContador() {
    const usuario = localStorage.getItem("usuario");
    const contador = document.getElementById("contador");

    if (!contador) return;

    if (dados[usuario].pro) {
        contador.textContent = "🔥 Plano PRO ativo (ilimitado)";
    } else {
        contador.textContent =
            "Plano FREE: até 3 verificações por dia";
    }
}

// ================= PAGAMENTO =================

async function gerarPagamento() {
    const usuario = localStorage.getItem("usuario");

    const res = await fetch("/criar_pagamento", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ usuario })
    });

    const data = await res.json();

    if (data.status === "ok") {

        document.getElementById("qrCode").src =
            "data:image/png;base64," + data.qr_code_base64;

        document.getElementById("qrCode").style.display = "block";

        document.getElementById("pixCode").value = data.pix;
        document.getElementById("pixCode").style.display = "block";

    } else {
        alert("Erro ao gerar pagamento");
    }
}

// ================= SALVAR =================

function salvar() {
    localStorage.setItem("detectorg", JSON.stringify(dados));
}

window.onload = verificarLogin;
