import pandas as pd
import spacy
from spacy.tokens import DocBin
from sklearn.model_selection import train_test_split

# -------------------------------
# CONFIGURAÇÕES
# -------------------------------
CSV_INPUT = "nomes.csv"
TRAIN_OUTPUT = "train.spacy"
DEV_OUTPUT = "dev.spacy"
NLP = spacy.blank("pt")


def criar_entidades(texto, nome, sobrenome):
    """
    Retorna lista de entidades no formato spaCy:
    [(start, end, label), ...]
    """
    entidades = []
    start_index = 0

    # Nome
    if nome:
        idx = texto.lower().find(nome.lower())
        if idx != -1:
            entidades.append((idx, idx + len(nome), "GIVEN_NAME"))

    # Sobrenome
    if sobrenome:
        idx = texto.lower().find(sobrenome.lower())
        if idx != -1:
            entidades.append((idx, idx + len(sobrenome), "SURNAME"))

    return entidades


def gerar_spacy_dataset(df, output_file):
    doc_bin = DocBin()
    for _, row in df.iterrows():
        texto = row["nome_completo"]
        nome = row["nome"]
        sobrenome = row["sobrenome"]

        ents = criar_entidades(texto, nome, sobrenome)

        doc = NLP.make_doc(texto)
        spans = []

        for start, end, label in ents:
            span = doc.char_span(start, end, label=label)
            if span:
                spans.append(span)

        doc.ents = spans
        doc_bin.add(doc)

    doc_bin.to_disk(output_file)
    print(f"Gerado: {output_file}")


if __name__ == "__main__":
    df = pd.read_csv(CSV_INPUT)

    # Dividir treino/validação
    train_df, dev_df = train_test_split(df, test_size=0.15, random_state=42)

    gerar_spacy_dataset(train_df, TRAIN_OUTPUT)
    gerar_spacy_dataset(dev_df, DEV_OUTPUT)