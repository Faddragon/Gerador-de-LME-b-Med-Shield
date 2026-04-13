import os
from pypdf import PdfReader, PdfWriter
from datetime import datetime

def preencher_quadradinhos(dicionario, base_nome, valor, tamanho):
    """Auxiliar para distribuir caracteres em campos numerados (ex: peso_1, peso_2)"""
    if not valor: return
    valor_limpo = str(valor).replace(".", "").replace("-", "").replace("/", "").zfill(tamanho)
    for i, char in enumerate(valor_limpo):
        if i < tamanho:
            dicionario[f"{base_nome}_{i+1}"] = char

def gerar_lme_hospitalar(dados_extraidos):
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Apontando OBRIGATORIAMENTE para o PDF com as caixinhas interativas
    caminho_template = os.path.join(base_path, "public", "lme_editavel.pdf") 
    pasta_saida = os.path.join(base_path, "output")

    if not os.path.exists(pasta_saida): 
        os.makedirs(pasta_saida)

    # Trava de segurança para avisar se o arquivo errado estiver na pasta
    if not os.path.exists(caminho_template):
        print(f"ERRO: O arquivo {caminho_template} não foi encontrado!")
        return None

    try:
        reader = PdfReader(caminho_template)
        
        # Trava de segurança para checar se o PDF tem formulários
        if "/AcroForm" not in reader.trailer["/Root"]:
            print("ERRO FATAL: O PDF lme_editavel.pdf não possui campos de formulário! Salve-o novamente no seu editor de PDF garantindo que as caixas de texto interativas sejam mantidas.")
            return None

        writer = PdfWriter()
        writer.append(reader)

        # 2. Sincronizado EXATAMENTE com o que seu terminal mostrou
        campos_final = {
            "nome_paciente": dados_extraidos.get("nome_paciente", ""),
            "nome_mae":      dados_extraidos.get("nome_mae", ""),
            "medicamento":   dados_extraidos.get("medicamento_linha_1", ""), 
            "qtd_1":         dados_extraidos.get("quantidade", ""),
            "qtd_2":         dados_extraidos.get("quantidade_2", ""),
            "qtd_3":         dados_extraidos.get("quantidade_3", ""),
            "anamnese":      dados_extraidos.get("anamnese", ""),
            "diagnostico":   dados_extraidos.get("diagnostico_nome", ""),
            "medico_nome":   dados_extraidos.get("nome_medico", ""),     
            "estabelecimento_nome": dados_extraidos.get("estabelecimento_nome", ""),
            "estabelecimento_cnes": dados_extraidos.get("estabelecimento_cnes", "")
        }

        # Distribuição nos quadradinhos
        preencher_quadradinhos(campos_final, "peso", dados_extraidos.get("peso", ""), 3)
        preencher_quadradinhos(campos_final, "alt",  dados_extraidos.get("altura", ""), 3)
        preencher_quadradinhos(campos_final, "cid",  dados_extraidos.get("cid_10", ""), 4)
        preencher_quadradinhos(campos_final, "cns",  dados_extraidos.get("medico_cns", ""), 15)
        preencher_quadradinhos(campos_final, "cnes", dados_extraidos.get("estabelecimento_cnes", ""), 7)
        

        # Injeta tudo no PDF
        writer.update_page_form_field_values(writer.pages[0], campos_final)

        nome_paciente = str(dados_extraidos.get("nome_paciente", "Paciente")).strip()[:15].replace(' ','_')
        timestamp = datetime.now().strftime('%d%m%Y_%H%M')
        nome_arq = f"LME_{nome_paciente}_{timestamp}.pdf"
        caminho_final = os.path.join(pasta_saida, nome_arq)
        
        with open(caminho_final, "wb") as f:
            writer.write(f)
        
        print(f"LME Gerada com SUCESSO -> Paciente: {nome_paciente}")
        return caminho_final

    except Exception as e:
        print(f"Erro no preenchimento: {e}")
        return None