# scripts/3_gerar_banco_js.py
import pandas as pd
import json
import os
import math

# 1. Navegação de pastas inteligente (Caminhos Relativos)
# Pega a pasta atual (scripts) e sobe um nível para a raiz do projeto
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.dirname(DIRETORIO_ATUAL)

# 2. Define onde buscar os dados e onde entregar o JS
ARQUIVO_EXCEL = os.path.join(RAIZ_PROJETO, "data", "banco_dados_lme_com_anamnese.xlsx")
ARQUIVO_JS = os.path.join(RAIZ_PROJETO, "public", "banco_dados.js")

def converter_excel_para_js():
    print(f"Buscando arquivo em: {ARQUIVO_EXCEL}")
    
    if not os.path.exists(ARQUIVO_EXCEL):
        print("ERRO: Arquivo Excel não encontrado.")
        print("Certifique-se de que o arquivo 'banco_dados_lme_com_anamnese.xlsx' está dentro da pasta 'data'.")
        return

    try:
        # Lê a planilha do Excel
        df = pd.read_excel(ARQUIVO_EXCEL)
        
        # O Pandas transforma células vazias em NaN. Precisamos converter para string vazia ""
        # para que o JavaScript não quebre tentando ler o JSON.
        df = df.fillna("")
        
        # Converte o DataFrame para uma lista de dicionários padrão Python
        dados = df.to_dict(orient='records')
        
        # Gera o arquivo JavaScript na pasta 'public'
        with open(ARQUIVO_JS, 'w', encoding='utf-8') as f:
            f.write("// ========================================================\n")
            f.write("// Banco de Dados gerado automaticamente pelo Python\n")
            f.write("// NÃO EDITE ESTE ARQUIVO MANUALMENTE.\n")
            f.write("// ========================================================\n\n")
            f.write("const bancoDeDados = " + json.dumps(dados, ensure_ascii=False, indent=4) + ";\n")
            
        print(f"\n[SUCESSO] O cérebro da plataforma foi gerado na pasta public: {ARQUIVO_JS}")
        print("O seu frontend web está atualizado e pronto para uso!")

    except ImportError:
        print("ERRO: Faltam bibliotecas. Por favor, execute: pip install pandas openpyxl")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    converter_excel_para_js()