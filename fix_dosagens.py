import pandas as pd
import re


def normalizar(s):
    s = str(s)
    s = s.replace("\ufffd", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def processar_dosagens(dosagens_str):
    if not dosagens_str or pd.isna(dosagens_str):
        return ""

    s = normalizar(dosagens_str)

    # Ja tem |
    if "|" in s:
        return s

    # Tem ;
    if ";" in s:
        return s.replace("; ", "|").replace(";", "|")

    # PROTEGE DECIMAIS: substitui "0,25" -> "0DECIMAL25", "2,5" -> "2DECIMAL5"
    s = re.sub(r"(\d),(\d)", r"\1DECIMAL\2", s)

    # Padrao: "X mg e Y mg - apresentacao"
    match = re.search(r"(.+?)[\-–—](.+)$", s)
    if match:
        doses_parte = match.group(1).strip()
        apres = match.group(2).strip()

        # Separa doses com ' e ' ou ', '
        doses_lista = re.split(r",\s*|\s+e\s+", doses_parte)

        if len(doses_lista) > 1:
            resultado = []
            for d in doses_lista:
                d = d.strip()
                if d:
                    # Restaura decimal
                    d = re.sub(r"(\d)DECIMAL(\d)", r"\1,\2", d)
                    resultado.append(f"{d} - {apres}")
            return "|".join(resultado)

    # Padrao: "0,25 mcg - cpsula, 0,50 mcg - cpsula"
    if ", " in s:
        partes = s.split(", ")
        if len(partes) > 1:
            apres_encontrada = None
            doses_validas = []
            for p in partes:
                p = p.strip()
                match2 = re.search(r"(.+?)[\-–—](.+)$", p)
                if match2:
                    doses_validas.append(p)
                    apres_encontrada = match2.group(2).strip()

            if len(doses_validas) == len(partes) and apres_encontrada:
                # Restaura decimal em cada uma
                result = []
                for d in doses_validas:
                    d = re.sub(r"(\d)DECIMAL(\d)", r"\1,\2", d)
                    result.append(d)
                return "|".join(result)

    # Restaura decimal se nao separou
    s = re.sub(r"(\d)DECIMAL(\d)", r"\1,\2", s)
    return s


# Ler
df = pd.read_excel(r"bmed-lme-app\data\banco_dados_lme_com_anamnese.xlsx")

# Aplicar
df["dosagens_array"] = df["dosagens_apresentacoes"].apply(processar_dosagens)

# Salvar
df.to_excel(r"bmed-lme-app\data\banco_dados_lme_com_anamnese.xlsx", index=False)

# Testar
print("=== CALCITRIOL ===")
cal = df[df["medicamento"].str.contains("Calcitriol", na=False)]
for i, row in cal.iterrows():
    print(f"{row['medicamento']} - {row['diagnosticos']}")
    print(f"  Original: {row['dosagens_apresentacoes']}")
    print(f"  Novo: {row['dosagens_array']}")
    print()
