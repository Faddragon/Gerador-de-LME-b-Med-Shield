// ==========================================
// 1. CARREGAMENTO DO BANCO DE DADOS
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    const selectMed = document.getElementById("select_medicamento");

    // Verifica se o bancoDeDados foi carregado corretamente
    if (typeof bancoDeDados === 'undefined') {
        alert("Erro: Banco de dados não carregado. Certifique-se de rodar o script Python primeiro.");
        return;
    }

    // Organiza a lista em ordem alfabética
    bancoDeDados.sort((a, b) => (a.medicamento || "").localeCompare(b.medicamento || ""));

    bancoDeDados.forEach((item, index) => {
        if (item.medicamento && item.diagnosticos) {
            let opt = document.createElement("option");
            opt.value = index;
            opt.textContent = `${item.medicamento} - ${item.diagnosticos}`;
            selectMed.appendChild(opt);
        }
    });
});

// ==========================================
// 2. DINÂMICA DOS DROPDOWNS
// ==========================================
function atualizarDiagnosticos() {
    const selectMed = document.getElementById("select_medicamento");
    const selectDosagem = document.getElementById("select_dosagem");
    const selectCid = document.getElementById("select_cid");
    const id = selectMed.value;

    selectCid.innerHTML = '<option value="">Selecione o CID...</option>';
    selectDosagem.innerHTML = '<option value="">Selecione a dosagem...</option>';
    document.getElementById("texto_anamnese").value = "";

    if (id !== "") {
        selectCid.disabled = false;
        selectDosagem.disabled = false;

        // Preencher dropdown de dosagens
        let dosagensBrutas = bancoDeDados[id].dosagens_apresentacoes || "";
        let dosagensArray = processarDosagens(dosagensBrutas);

        dosagensArray.forEach(dosagem => {
            let opt = document.createElement("option");
            opt.value = dosagem;
            opt.textContent = dosagem;
            selectDosagem.appendChild(opt);
        });

        // Auto-selecionar se só houver uma opção
        if (dosagensArray.length === 1) {
            selectDosagem.value = dosagensArray[0];
        }

        let cidsBrutos = bancoDeDados[id].cids_contemplados || "";
        let cidsArray = cidsBrutos.split(',').map(c => c.trim()).filter(c => c);

        cidsArray.forEach(cid => {
            let opt = document.createElement("option");
            opt.value = cid;
            opt.textContent = `${cid} - ${bancoDeDados[id].diagnosticos}`;
            selectCid.appendChild(opt);
        });
    } else {
        selectCid.disabled = true;
        selectDosagem.disabled = true;
    }
}

function processarDosagens(dosagensStr) {
    if (!dosagensStr) return [];
    
    // Separa por vírgula, mas evita separator dentro de números decimais (ex: 0,5 mg)
    let dosagens = [];
    let atual = "";
    let virgulaCount = 0;
    
    for (let i = 0; i < dosagensStr.length; i++) {
        let char = dosagensStr[i];
        if (char === ',') {
            virgulaCount++;
        }
        if (virgulaCount === 1 && char === ',') {
            if (atual.trim()) {
                dosagens.push(atual.trim());
            }
            atual = "";
            virgulaCount = 0;
        } else {
            atual += char;
        }
    }
    if (atual.trim()) {
        dosagens.push(atual.trim());
    }
    
    // Se não conseguiu separar, tenta por ponto e vírgula
    if (dosagens.length <= 1 && dosagensStr.includes(';')) {
        dosagens = dosagensStr.split(';').map(d => d.trim()).filter(d => d);
    }
    
    return dosagens;
}

function gerarAnamnesePadrao() {
    const id = document.getElementById("select_medicamento").value;
    if (id !== "") {
        document.getElementById("texto_anamnese").value = bancoDeDados[id].anamnese_padrao || "";
    }
}

// ==========================================
// 3. SMART PASTE (ALGORITMO MULTIFORMATO)
// ==========================================
function extrairDadosProntuario() {
    const texto = document.getElementById("texto_prontuario").value;
    if (!texto) return alert("Por favor, cole o cabeçalho do prontuário na caixa.");

    let cpfEncontrado = "";
    let cnsEncontrado = "";
    let nomeEncontrado = "";
    let maeEncontrada = "";

    const linhas = texto.split('\n').map(l => l.trim()).filter(l => l.length > 0);

    for (let i = 0; i < linhas.length; i++) {
        let linhaAtual = linhas[i].toUpperCase();

        if (/^(NOME DE REGISTRO|NOME DO PACIENTE|NOME|PACIENTE)$/.test(linhaAtual) && i + 1 < linhas.length) {
            nomeEncontrado = linhas[i + 1];
        } else if (/^(NOME DE REGISTRO|NOME DO PACIENTE|NOME|PACIENTE)\s*:/.test(linhaAtual)) {
            nomeEncontrado = linhaAtual.split(':')[1].trim();
        }

        if (/^(MÃE|MAE|NOME DA MÃE|FILIAÇÃO)$/.test(linhaAtual) && i + 1 < linhas.length) {
            maeEncontrada = linhas[i + 1];
        } else if (/^(MÃE|MAE|NOME DA MÃE|FILIAÇÃO)\s*:/.test(linhaAtual)) {
            maeEncontrada = linhaAtual.split(':')[1].trim();
        }

        if (/^CPF$/.test(linhaAtual) && i + 1 < linhas.length) {
            let tempCpf = linhas[i + 1].replace(/[^\d]/g, '');
            if (tempCpf.length === 11) cpfEncontrado = tempCpf;
        } else if (/^CPF\s*:/.test(linhaAtual)) {
            let tempCpf = linhaAtual.replace(/[^\d]/g, '');
            if (tempCpf.length === 11) cpfEncontrado = tempCpf;
        }

        if (/^CNS$/.test(linhaAtual) && i + 1 < linhas.length) {
            let tempCns = linhas[i + 1].replace(/[^\d]/g, '');
            if (tempCns.length === 15) cnsEncontrado = tempCns;
        } else if (/^CNS\s*:/.test(linhaAtual)) {
            let tempCns = linhaAtual.replace(/[^\d]/g, '');
            if (tempCns.length === 15) cnsEncontrado = tempCns;
        }
    }

    if (!cpfEncontrado) {
        const matchCPF = texto.match(/\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b/);
        if (matchCPF) cpfEncontrado = matchCPF[0].replace(/[^\d]/g, '');
    }

    if (!cnsEncontrado) {
        const matchCNS = texto.match(/\b[12789]\d{14}\b/);
        if (matchCNS) cnsEncontrado = matchCNS[0];
    }

    if (nomeEncontrado) document.getElementById("paciente_nome").value = nomeEncontrado.toUpperCase();
    if (maeEncontrada) document.getElementById("paciente_mae").value = maeEncontrada.toUpperCase();
    if (cpfEncontrado) document.getElementById("paciente_cpf").value = cpfEncontrado.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
    if (cnsEncontrado) document.getElementById("paciente_cns").value = cnsEncontrado;

    document.getElementById("texto_prontuario").value = "";
    document.getElementById("texto_prontuario").placeholder = "Extração concluída! Confira os dados nos campos abaixo.";
}

// ==========================================
// 5. MOTOR DO MODAL E GERAÇÃO DA LME
// ==========================================

// A. Abre o Modal de Segurança e carrega o PDF/Exigências
function gerarPDFLME() {
    const selectMed = document.getElementById("select_medicamento");
    const selectDosagem = document.getElementById("select_dosagem");
    const id = selectMed.value;

    if (id === "" || !document.getElementById("paciente_nome").value) {
        return alert("Atenção: O Nome do Paciente e a seleção de Medicamento são obrigatórios.");
    }

    if (!selectDosagem.value) {
        return alert("Atenção: Por favor, selecione a Dosagem/Apresentação do medicamento.");
    }

    const dadosProtocolo = bancoDeDados[id];

    // Preenche o modal
    document.getElementById("alerta_medicamento").innerText = dadosProtocolo.medicamento;
    // --- FORMATADOR INTELIGENTE DE EXAMES ---
    let examesBrutos = dadosProtocolo.exames_e_criterios_obrigatorios || "";

    if (examesBrutos.trim() !== "") {
        // Corta o texto no ponto e vírgula (;), limpa espaços e remove partes vazias
        let listaExames = examesBrutos.split(';').map(item => item.trim()).filter(item => item.length > 0);

        // Constrói uma lista pontuada em HTML
        let htmlLista = '<ul class="mb-0 ps-3" style="text-align: left; list-style-type: disc;">';
        listaExames.forEach(exame => {
            // Garante que a primeira letra seja maiúscula para ficar bonito
            let exameFormatado = exame.charAt(0).toUpperCase() + exame.slice(1);
            htmlLista += `<li class="mb-1 pb-1 border-bottom border-light">${exameFormatado}.</li>`;
        });
        htmlLista += '</ul>';

        // Injeta o HTML renderizado na tela (usando innerHTML em vez de innerText)
        document.getElementById("alerta_exames").innerHTML = htmlLista;
    } else {
        document.getElementById("alerta_exames").innerHTML = "Nenhum exame específico listado na base.";
    }
    // ----------------------------------------
    document.getElementById("alerta_tratamento").innerText = dadosProtocolo.tratamento_previo_exigido || "Não há exigência de falha terapêutica prévia.";

    // Lógica do PDF Embutido
    const areaPdf = document.getElementById("area_pdf_governo");
    const iframePdf = document.getElementById("iframe_pdf_protocolo");

    if (dadosProtocolo.arquivo_origem && dadosProtocolo.arquivo_origem !== "") {
        iframePdf.src = `/pdfs/${dadosProtocolo.arquivo_origem}`;
        areaPdf.style.display = "block";
    } else {
        iframePdf.src = "";
        areaPdf.style.display = "none";
    }

    // Reseta os checkboxes e desabilita botão verde ao abrir
    document.querySelectorAll('.check-auditoria').forEach(check => check.checked = false);
    document.getElementById('btn_gerar_seguro').disabled = true;

    // Exibe o Pop-up na tela
    const modalTracker = new bootstrap.Modal(document.getElementById('modalOrientacoes'));
    modalTracker.show();
}

// B. Validador das Caixinhas de Auditoria do Modal
function verificarCheckboxes() {
    const checks = document.querySelectorAll('.check-auditoria');
    const btnGerarSeguro = document.getElementById('btn_gerar_seguro');

    let todosMarcados = true;
    checks.forEach(check => {
        if (!check.checked) todosMarcados = false;
    });

    btnGerarSeguro.disabled = !todosMarcados;
}

// C. Confirma os avisos e envia os dados para o servidor gerar a LME final
async function confirmarEGerarPDF() {
    const selectMed = document.getElementById("select_medicamento");
    const selectDosagem = document.getElementById("select_dosagem");
    const id = selectMed.value;

    let nomeMed = bancoDeDados[id].medicamento || "";
    let dosagemSelecionada = selectDosagem.value || bancoDeDados[id].dosagens_apresentacoes || "";
    let diagnosticoNome = bancoDeDados[id].diagnosticos || "";
    let medicamentoComDose = `${nomeMed} - ${dosagemSelecionada}`;

    const dados = {
        "nome_paciente": document.getElementById("paciente_nome").value.toUpperCase(),
        "nome_mae": document.getElementById("paciente_mae").value.toUpperCase(),
        "cpf": document.getElementById("paciente_cpf").value,
        "cns_paciente": document.getElementById("paciente_cns").value,
        "peso": document.getElementById("paciente_peso").value,
        "altura": document.getElementById("paciente_altura").value,

        // Campos novos capturados da tela
        "estabelecimento_nome": document.getElementById("estabelecimento_nome") ? document.getElementById("estabelecimento_nome").value.toUpperCase() : "",
        "estabelecimento_cnes": document.getElementById("estabelecimento_cnes") ? document.getElementById("estabelecimento_cnes").value : "",

        "medicamento_linha_1": medicamentoComDose,
        "quantidade": document.getElementById("medicamento_quantidade") ? document.getElementById("medicamento_quantidade").value : "",
        "quantidade_2": document.getElementById("medicamento_quantidade_2") ? document.getElementById("medicamento_quantidade_2").value : "",
        "quantidade_3": document.getElementById("medicamento_quantidade_3") ? document.getElementById("medicamento_quantidade_3").value : "",

        "cid_10": document.getElementById("select_cid").value,
        "diagnostico_nome": diagnosticoNome,
        "anamnese": document.getElementById("texto_anamnese").value,

        "nome_medico": document.getElementById("medico_nome") ? document.getElementById("medico_nome").value.toUpperCase() : "",
        "medico_cns": document.getElementById("medico_cns") ? document.getElementById("medico_cns").value : ""
    };

    try {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/gerar_lme_html';
        form.target = '_blank';

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'dados_json';
        input.value = JSON.stringify(dados);

        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);

        // Tenta fechar o modal suavemente após abrir a nova aba da LME
        const modalElement = document.getElementById('modalOrientacoes');
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }

    } catch (error) {
        console.error("Erro:", error);
        alert("Erro ao abrir a LME.");
    }
}