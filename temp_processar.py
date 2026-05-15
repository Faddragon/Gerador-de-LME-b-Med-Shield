import pandas as pd

# Ler Excel
df = pd.read_excel(
    r"F:\backup ferramentas\Ferramenta LME_para github\bmed-lme-app\data\banco_dados_lme_com_anamnese.xlsx"
)

# Criar nova coluna simples - apenas copia o que já existe
# O código JS vai detectar | primeiro, senão usa vírgula
df["dosagens_array"] = df["dosagens_apresentacoes"].fillna("")

# Salvar
df.to_excel(
    r"F:\backup ferramentas\Ferramenta LME_para github\bmed-lme-app\data\banco_dados_lme_com_anamnese.xlsx",
    index=False,
)

print("Coluna dosagens_array criada!")
print("Origem: mesma coluna dosagens_apresentacoes")
print("O código JS vai detectar | como separador primário")
print()
print("Para funcionar, use | nos casos especiais no Excel")
print("Exemplo: 100 mg - cpsula|200 mg - cpsula")
