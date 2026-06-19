import streamlit as st
import pandas as pd
from io import BytesIO

st.title("📊 Gerador de Planilha de Notas")

arquivo = st.file_uploader("Envie o arquivo Base.xlsx", type=["xlsx"])

if arquivo:

    df = pd.read_excel(arquivo, engine="openpyxl")

    df = df.rename(columns={
        "NOME_COMPL": "Nome",
        "TURMA": "Turma",
        "NOME_DISCIPLINA": "Disciplina",
        "MA": "Nota"
    })

    df["ordem"] = df.groupby(["Nome", "Turma"]).cumcount() + 1

    df_pivot = df.pivot(index=["Nome", "Turma"], columns="ordem", values=["Disciplina", "Nota"])
    df_pivot.columns = [f"{tipo}_{i}" for tipo, i in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    colunas = ["Nome", "Turma"]
    max_ordem = df["ordem"].max()

    for i in range(1, max_ordem + 1):
        colunas.append(f"Disciplina_{i}")
        colunas.append(f"Nota_{i}")

    df_final = df_pivot[colunas]

    # ✅ SEU AJUSTE (mantido)
    novos_nomes = {}
    for i in range(1, max_ordem + 1):
        col_disc = f"Disciplina_{i}"
        if col_disc in df_final.columns:
            valores = df_final[col_disc].dropna()
            if not valores.empty:
                novos_nomes[col_disc] = valores.iloc[0]

    df_final = df_final.rename(columns=novos_nomes)

    # tratar notas
    colunas_notas = [col for col in df_final.columns if "Nota_" in col]
    df_final[colunas_notas] = df_final[colunas_notas].apply(pd.to_numeric, errors='coerce')

    # destaque
    df_final["Destaque"] = df_final[colunas_notas].ge(40).all(axis=1).apply(
        lambda x: "Estudante Destaque" if x else ""
    )

    st.success("✅ Processamento concluído!")
    st.dataframe(df_final)

    # botão download
    output = BytesIO()
    df_final.to_excel(output, index=False, engine="openpyxl")

    st.download_button(
        label="📥 Baixar planilha",
        data=output.getvalue(),
        file_name="Planilha_ok.xlsx"
    )