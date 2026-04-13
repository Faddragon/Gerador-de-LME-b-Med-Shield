import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def construir_banco_e_tabela_ses_sp():
    url_base = "https://saude.sp.gov.br/ses/perfil/gestor/assistencia-farmaceutica/medicamentos-dos-componentes-da-assistencia-farmaceutica/links-do-componente-especializado-da-assistencia-farmaceutica/relacao-estadual-de-medicamentos-do-componente-especializado-da-assistencia-farmaceutica/consulta-por-medicamento"
    pasta_destino = "pdfs_bmed_alto_custo"
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Mapeando a página principal...")
    try:
        resposta_principal = requests.get(url_base, headers=headers, timeout=20)
        resposta_principal.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar a página principal: {e}")
        return

    sopa_principal = BeautifulSoup(resposta_principal.content, 'html.parser')
    todos_links = sopa_principal.find_all('a')
    links_medicamentos = {}
    
    for link in todos_links:
        href = link.get('href')
        if href and not href.startswith('#') and not href.startswith('javascript'):
            url_completa_med = urljoin(url_base, href)
            nome_med = link.text.strip()
            if nome_med and len(nome_med) > 2: 
                links_medicamentos[url_completa_med] = nome_med

    # Lista que vai armazenar os dados para a nossa tabela
    dados_tabela = []
    pdfs_baixados = 0

    for url_med, nome_med in links_medicamentos.items():
        print(f"\nInvestigando: {nome_med} -> {url_med}")
        
        try:
            resp_med = requests.get(url_med, headers=headers, timeout=20)
            sopa_med = BeautifulSoup(resp_med.content, 'html.parser')
            links_pdfs = sopa_med.find_all('a')
            
            for link_pdf in links_pdfs:
                href_pdf = link_pdf.get('href')
                
                if href_pdf and href_pdf.lower().endswith('.pdf'):
                    url_completa_pdf = urljoin(url_med, href_pdf)
                    nome_arquivo = url_completa_pdf.split('/')[-1].split('?')[0]
                    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
                    
                    # Adiciona os metadados na nossa lista, mesmo se o arquivo já existir
                    dados_tabela.append({
                        "Medicamento": nome_med,
                        "Nome_do_Arquivo_PDF": nome_arquivo,
                        "Doencas_CIDs": "",  # A ser preenchido via NLP depois
                        "Caminho_Local": caminho_arquivo,
                        "URL_Origem": url_completa_pdf
                    })
                    
                    if os.path.exists(caminho_arquivo):
                        print(f"  [-] O PDF '{nome_arquivo}' já existe. Registrado na tabela.")
                        continue
                        
                    print(f"  [+] Baixando: {nome_arquivo}")
                    resp_pdf = requests.get(url_completa_pdf, headers=headers, timeout=30)
                    with open(caminho_arquivo, 'wb') as arquivo:
                        arquivo.write(resp_pdf.content)
                        
                    pdfs_baixados += 1
                    time.sleep(1.5)
                    
            time.sleep(2) 
            
        except Exception as e:
            print(f"  [!] Falha ao processar {nome_med}: {e}")

    # Transformando a lista em um DataFrame do pandas e exportando
    df_pdfs = pd.DataFrame(dados_tabela)
    
    # Removendo possíveis duplicatas caso um mesmo PDF apareça em dois links
    df_pdfs = df_pdfs.drop_duplicates(subset=['Nome_do_Arquivo_PDF'])
    
    caminho_csv = 'indice_medicamentos_ses.csv'
    df_pdfs.to_csv(caminho_csv, index=False, encoding='utf-8-sig')

    print(f"\nExtração concluída! Total baixado: {pdfs_baixados}")
    print(f"Tabela gerada com sucesso: '{caminho_csv}' com {len(df_pdfs)} registros.")

if __name__ == "__main__":
    construir_banco_e_tabela_ses_sp()