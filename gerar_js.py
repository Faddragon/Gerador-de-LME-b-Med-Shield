import pandas as pd
import json
import os

# ==========================================
# CONFIGURAÇÃO DE CAMINHOS
# ==========================================
# Onde a IA salvou o Excel:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_EXCEL = os.path.join(BASE_DIR, "banco_dados_lme.xlsx")

# Onde o seu servidor web precisa do arquivo .js (Ajuste se a pasta for diferente):
ARQUIVO_JS = os.path.join(BASE_DIR, "bmed-lme-app", "public", "banco_dados.js")

def converter_excel_para_js():
    print("Iniciando conversão do Excel para JavaScript...")
    
    if not os.path.exists(ARQUIVO_EXCEL):
        print(f"[X] Erro: O arquivo {ARQUIVO_EXCEL} não foi encontrado!")
        print("Rode o script da OpenAI primeiro para gerar o Excel.")
        return

    try:
        # 1. Lê a planilha de auditoria
        df = pd.read_excel(ARQUIVO_EXCEL)
        
        # 2. Limpa valores nulos (Transforma NaN em texto vazio para não quebrar o JS)
        df = df.fillna("")
        
        # Opcional: Filtra apenas as linhas que NÃO precisam de revisão manual urgente
        # df = df[df['necessita_revisao_manual'] == False]
        
        # 3. Converte a tabela para o formato JSON que o navegador entende
        dados_json = df.to_dict(orient='records')
        
        # 4. Envolve os dados na variável que o nosso app_logic.js está esperando
        conteudo_js = f"const bancoDeDados = {json.dumps(dados_json, indent=4, ensure_ascii=False)};"
        
        # 5. Salva direto na pasta do servidor web
        os.makedirs(os.path.dirname(ARQUIVO_JS), exist_ok=True)
        with open(ARQUIVO_JS, 'w', encoding='utf-8') as f:
            f.write(conteudo_js)
            
        print(f"[+] Sucesso Absoluto! O radar de medicamentos foi atualizado no sistema.")
        print(f"Arquivo gerado em: {ARQUIVO_JS}")
        print("Pode abrir o navegador e testar a plataforma b-Med!")

    except Exception as e:
        print(f"[X] Erro durante a conversão: {e}")

if __name__ == "__main__":
    converter_excel_para_js()