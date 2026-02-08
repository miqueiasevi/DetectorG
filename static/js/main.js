// ================= CONFIG =================
const LIMITE_DIARIO = 3;
const DURACAO_PRO = 30 * 24 * 60 * 60 * 1000; // 30 dias

// ================= LOGIN =================
function verificarLogin() {
  const usuario = localStorage.getItem("detectorG_usuario");
  if (!usuario) {
    window.location.href = "login.html";
    return;
  }

  const display = document.getElementById("usuarioLogado");
  if (display) display.textContent = "Usuário: " + usuario;

  const emailInput = document.getElementById("emailCliente");
  if (emailInput) emailInput.value = usuario;

  verificarExpiracao(usuario);
}

function fazerLogin() {
  const email = document.getElementById("emailLogin").value.trim();
  if (!email) {
    alert("❌ Digite seu e-mail");
    return;
  }
  localStorage.setItem("detectorG_usuario", email);
  window.location.href = "index.html";
}

function logout() {
  localStorage.removeItem("detectorG_usuario");
  window.location.href = "login.html";
}

// ================= ESTADO =================
const hoje = new Date().toLocaleDateString();
let dados = JSON.parse(localStorage.getItem("detectorg")) || {};
const usuarioAtual = localStorage.getItem("detectorG_usuario");

if (usuarioAtual && !dados[usuarioAtual]) {
  dados[usuarioAtual] = {
    data: hoje,
    usos: 0,
    pro: false,
    proFim: null,
    codigoUsado: null
  };
}

// ================= RESET DIÁRIO =================
function resetDiario(usuario) {
  if (dados[usuario].data !== hoje) {
    dados[usuario].data = hoje;
    dados[usuario].usos = 0;
    salvar();
  }
}

// ================= ANÁLISE DE AMEAÇAS =================
function analisarLink(link) {
  const url = link.toLowerCase();
  let riscos = [];
  let score = 0;

  // PHISHING
  const phishing = [
    "login", "verify", "secure", "account", "update",
    "premio", "conta", ".xyz", ".top", ".tk", ".info"
  ];
  phishing.forEach(p => {
    if (url.includes(p)) {
      riscos.push("Phishing");
      score += 30;
    }
  });

  // XSS
  const xss = [
    "<script", "javascript:", "onerror=",
    "onload=", "document.cookie", "%3cscript"
  ];
  xss.forEach(p => {
    if (url.includes(p)) {
      riscos.push("XSS");
      score += 40;
    }
  });

  // CSRF
  if (url.includes("csrf") || url.includes("token=")) {
    riscos.push("CSRF");
    score += 20;
  }

  // DRIVE-BY DOWNLOAD
  const downloads = [".exe", ".apk", ".msi", ".zip", ".rar"];
  downloads.forEach(ext => {
    if (url.includes(ext)) {
      riscos.push("Drive-by Download");
      score += 50;
    }
  });

  let nivel = "🟢 Baixo";
  if (score >= 30) nivel = "🟡 Médio";
  if (score >= 70) nivel = "🔴 Alto";

  return {
    nivel,
    riscos: [...new Set(riscos)]
  };
}

// ================= VERIFICAR LINK =================
function verificarLink() {
  const usuario = localStorage.getItem("detectorG_usuario");
  if (!usuario) {
    window.location.href = "login.html";
    return;
  }

  resetDiario(usuario);

  const link = document.getElementById("link").value.trim();
  const resultado = document.getElementById("resultado");
  const contador = document.getElementById("contador");

  if (!link) {
    resultado.textContent = "❌ Cole um link válido.";
    return;
  }

  if (!dados[usuario].pro && dados[usuario].usos >= LIMITE_DIARIO) {
    resultado.textContent = "🚫 Limite diário atingido. Assine o PRO.";
    return;
  }

  const analise = analisarLink(link);

  if (analise.riscos.length === 0) {
    resultado.textContent = "✅ Link seguro (nenhuma ameaça detectada)";
  } else {
    resultado.innerHTML =
      `${analise.nivel} RISCO DETECTADO<br>` +
      `Ameaças: ${analise.riscos.join(", ")}`;
  }

  if (!dados[usuario].pro) {
    dados[usuario].usos++;
    contador.textContent = `Uso gratuito: ${dados[usuario].usos}/${LIMITE_DIARIO}`;
  } else {
    contador.textContent = "Plano PRO ativo (ilimitado)";
  }

  salvar();
}

// ================= PAGAMENTO / PIX =================
function abrirPagamento() {
  document.getElementById("pagamento").classList.remove("hidden");
}
function fecharPagamento() {
  document.getElementById("pagamento").classList.add("hidden");
}
function copiarPix() {
  const pix = document.getElementById("pixKey");
  pix.select();
  pix.setSelectionRange(0, 99999);
  document.execCommand("copy");
  alert("✅ Chave Pix copiada!");
}

// ================= SOLICITAR CÓDIGO =================
function solicitarCodigo() {
  const usuario = localStorage.getItem("detectorG_usuario");
  if (!usuario) return;

  const mensagem =
    `Pagamento Plano PRO - DetectorG\n\n` +
    `Email do cliente: ${usuario}\n\n` +
    `Já realizei o pagamento via PIX. Solicito o código PRO.`;

  navigator.clipboard.writeText(mensagem).then(() => {
    alert("✅ Solicitação copiada!\nEnvie por e-mail para detectorgdetectorg@gmail.com");
  });
}

// ================= ATIVAR PRO =================
function ativarPRO() {
  const usuario = localStorage.getItem("detectorG_usuario");
  if (!usuario) return;

  const codigo = document.getElementById("codigoPRO").value.trim();
  if (!codigo) {
    alert("❌ Digite o código PRO");
    return;
  }

  dados[usuario].pro = true;
  dados[usuario].proFim = Date.now() + DURACAO_PRO;
  dados[usuario].codigoUsado = codigo;

  salvar();
  alert("✅ Plano PRO ativado por 30 dias!");
  fecharPagamento();
}

// ================= EXPIRAÇÃO PRO =================
function verificarExpiracao(usuario) {
  if (dados[usuario].pro && dados[usuario].proFim && Date.now() > dados[usuario].proFim) {
    dados[usuario].pro = false;
    dados[usuario].proFim = null;
    dados[usuario].codigoUsado = null;
    salvar();
    alert("⚠️ Seu plano PRO expirou.");
  }
}

// ================= EXCLUIR CONTA =================
function excluirConta() {
  const usuario = localStorage.getItem("detectorG_usuario");
  if (!usuario) return;

  if (!confirm("⚠️ Deseja excluir sua conta? Todos os dados serão apagados.")) return;

  delete dados[usuario];
  salvar();
  localStorage.removeItem("detectorG_usuario");

  alert("✅ Conta excluída com sucesso!");
  window.location.href = "login.html";
}

// ================= SALVAR =================
function salvar() {
  localStorage.setItem("detectorg", JSON.stringify(dados));
}

// ================= INICIAL =================
window.onload = verificarLogin;
