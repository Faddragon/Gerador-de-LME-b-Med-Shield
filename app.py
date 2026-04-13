import subprocess
import sys
import os
import time

# ==========================================
# 1. AUTO-INSTALADOR DE DEPENDÊNCIAS
# ==========================================
def instalar_dependencias():
    """Garante que todas as bibliotecas necessárias estejam instaladas antes de rodar."""
    dependencias = {
        'fitz': 'PyMuPDF',
        'pandas': 'pandas',
        'pydantic': 'pydantic',
        'openai': 'openai',
        'openpyxl': 'openpyxl' 
    }
    for modulo, pacote in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            print(f"Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])

instalar_dependencias()

# ==========================================
# 2. IMPORTAÇÕES E CONFIGURAÇÕES
# ==========================================
import fitz  # PyMuPDF
import pandas as pd
from pydantic import BaseModel, Field
from openai import OpenAI

# A chave deve estar configurada nas variáveis de ambiente como OPENAI_API_KEY
# Exemplo: os.environ["OPENAI_API_KEY"] = "sua-chave-aqui"
client = OpenAI()

# Caminhos relativos ao diretório atual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_PDFS = os.path.join(BASE_DIR, "pdfs_bmed_alto_custo")
ARQUIVO_SAIDA = os.path.join(BASE_DIR, "banco_dados_lme.xlsx")

# ==========================================
# 3. ESTRUTURA DO BANCO DE DADOS E GUARDRAILS
# ==========================================
class DadosLME(BaseModel):
    medicamento: str = Field(description="Nome do princípio ativo principal.")
    dosagens_apresentacoes: str = Field(description="Todas as dosagens e apresentações físicas disponíveis.")
    cids_contemplados: str = Field(description="Lista de todos os códigos CID-10 permitidos. Atente-se a restrições de idade.")
    diagnosticos: str = Field(description="Nomes das doenças correspondentes aos CIDs.")
    quantidade_maxima_mensal: str = Field(description="Posologia e quantidades máximas permitidas (separe dose inicial/ataque e manutenção, se houver).")
    exames_e_criterios_obrigatorios: str = Field(description="Exames laboratoriais, de imagem, sorologias e escalas (ex: EVA, LANSS) exclusivos da 1ª solicitação. Ignore exames de renovação.")
    tratamento_previo_exigido: str = Field(description="Descreva qual foi a falha terapêutica ou tratamento prévio exigido. Se não houver, escreva 'Não'.")
    
    # Guardrails de Segurança Médica
    necessita_revisao_manual: bool = Field(description="Retorne True se houver qualquer ambiguidade, texto cortado, contradição, ou se não tiver 100% de certeza. Caso contrário, retorne False.")
    motivo_revisao: str = Field(description="Se necessita_revisao_manual for True, explique resumidamente qual foi a dúvida. Se for False, deixe vazio.")

# ==========================================
# 4. ENGENHARIA DE PROMPT
# ==========================================
MENSAGEM_SISTEMA = """
Você é um Auditor Médico Sênior especialista nos Protocolos Clínicos e Diretrizes Terapêuticas (PCDT) do Componente Especializado da Assistência Farmacêutica (CEAF) do SUS de São Paulo.
Sua missão é extrair dados de PDFs governamentais para alimentar um banco de dados relacional focado no preenchimento automático do formulário LME.
Você deve ser cirúrgico, preciso e não inventar informações. 

REGRA DE OURO (GUARDRAIL):
A integridade médica deste banco de dados é crítica. É absolutamente inaceitável alucinar ou adivinhar informações. Se um texto estiver ambíguo, confuso, corrompido, ou se você tiver QUALQUER dúvida técnica sobre como interpretar a dose, os CIDs ou os exames obrigatórios, você deve OBRIGATORIAMENTE marcar o campo 'necessita_revisao_manual' como True e explicar sua dúvida no campo 'motivo_revisao'. Em caso de dúvida, prefira sinalizar para revisão humana do que preencher um dado incerto.
"""

MENSAGEM_USUARIO = """
Analise o documento clínico fornecido e extraia as informações estritamente de acordo com as seguintes regras de mapeamento:

1. medicamento: Extraia o nome do princípio ativo.
2. diagnosticos: Extraia a indicação clínica principal.
3. cids_contemplados: Liste todos os códigos CID-10 permitidos.
4. dosagens_apresentacoes: Liste todas as apresentações físicas disponíveis.
5. quantidade_maxima_mensal: Descreva a posologia e as quantidades máximas para dispensação e faturamento.
6. exames_e_criterios_obrigatorios: Liste exames e escalas exclusivas da '1ª Solicitação'. Ignore a renovação.
7. tratamento_previo_exigido: Descreva qual foi a falha exigida previamente, se houver.

TEXTO DO DOCUMENTO:
{texto_pdf}
"""

# ==========================================
# 5. FUNÇÕES DE PROCESSAMENTO
# ==========================================
def ler_texto_pdf(caminho_arquivo):
    """Abre o PDF local e extrai todo o texto."""
    try:
        doc = fitz.open(caminho_arquivo)
        texto = "".join([pagina.get_text() for pagina in doc])
        return texto
    except Exception as e:
        print(f"  [X] Erro ao ler PDF {caminho_arquivo}: {e}")
        return ""

def extrair_entidades_openai(texto_pdf):
    """Envia o texto para a OpenAI forçando a saída no esquema DadosLME."""
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": MENSAGEM_SISTEMA},
                {"role": "user", "content": MENSAGEM_USUARIO.format(texto_pdf=texto_pdf)}
            ],
            response_format=DadosLME,
            temperature=0.0 # Sem criatividade, apenas extração exata
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"  [X] Erro na API da OpenAI: {e}")
        return None

# ==========================================
# 6. MOTOR DE EXECUÇÃO EM LOTE
# ==========================================
def processar_pasta_pdfs():
    if not os.path.exists(DIRETORIO_PDFS):
        print(f"Erro: O diretório {DIRETORIO_PDFS} não foi encontrado.")
        return

    arquivos = [f for f in os.listdir(DIRETORIO_PDFS) if f.lower().endswith('.pdf')]
    total_arquivos = len(arquivos)
    
    if total_arquivos == 0:
        print(f"Nenhum arquivo PDF encontrado na pasta: {DIRETORIO_PDFS}")
        return
        
    print(f"Encontrados {total_arquivos} PDFs. Iniciando motor de auditoria IA...\n")
    
    dados_extraidos = []

    for index, arquivo in enumerate(arquivos):
        caminho_completo = os.path.join(DIRETORIO_PDFS, arquivo)
        print(f"[{index + 1}/{total_arquivos}] Analisando: {arquivo}")
        
        texto_pdf = ler_texto_pdf(caminho_completo)
        
        # Limita o texto aos primeiros 30.000 caracteres para economizar tokens e tempo
        # (As regras do CEAF estão quase sempre nas primeiras 3 a 5 páginas)
        texto_pdf = texto_pdf[:30000] 
        
        if len(texto_pdf.strip()) > 50:
            resultado = extrair_entidades_openai(texto_pdf)
            
            if resultado:
                linha = resultado.model_dump()
                linha['arquivo_origem'] = arquivo # Rastreabilidade
                dados_extraidos.append(linha)
                
                # Feedback visual de segurança
                if linha['necessita_revisao_manual']:
                    print(f"  [!] Extraído com ressalvas (Revisão Necessária): {linha.get('medicamento', 'Desconhecido')}")
                else:
                    print(f"  [+] Extraído com sucesso: {linha.get('medicamento', 'Desconhecido')}")
            
            # Pausa de 1.5 segundos para não sobrecarregar o Rate Limit da OpenAI
            time.sleep(1.5) 
        else:
            print("  [-] PDF vazio ou corrompido (possivelmente imagem escaneada sem texto).")

    # ==========================================
    # 7. GERAÇÃO DO BANCO DE DADOS (EXCEL)
    # ==========================================
    if dados_extraidos:
        df = pd.DataFrame(dados_extraidos)
        
        # Reorganizando as colunas para facilitar a leitura humana no Excel
        cols = [
            'medicamento', 
            'diagnosticos', 
            'cids_contemplados', 
            'dosagens_apresentacoes', 
            'quantidade_maxima_mensal', 
            'exames_e_criterios_obrigatorios', 
            'tratamento_previo_exigido', 
            'necessita_revisao_manual',
            'motivo_revisao',
            'arquivo_origem'
        ]
        
        # Garante que as colunas existam antes de reordenar
        df = df[[c for c in cols if c in df.columns]]
        
        df.to_excel(ARQUIVO_SAIDA, index=False)
        print(f"\nSucesso absoluto! O cérebro da plataforma b-Med foi gerado em: {ARQUIVO_SAIDA}")
        
        # Exibe um pequeno relatório de quantas revisões manuais serão necessárias
        revisoes = df['necessita_revisao_manual'].sum()
        print(f"Resumo da operação: {len(df)} protocolos processados. {revisoes} necessitam de revisão humana rápida.")
    else:
        print("\nNenhum dado foi extraído com sucesso.")

if __name__ == "__main__":
    processar_pasta_pdfs()