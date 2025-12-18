import argparse
import spacy
import os
import csv
from pathlib import Path

def carregar_modelo():
    # Ajuste o caminho se necessário
    return spacy.load("./modelo_nomes/model-best")

def separar_nome(modelo, nome_completo):
    doc = modelo(nome_completo)
    partes_nome = []
    partes_sobrenome = []

    for ent in doc.ents:
        if ent.label_ == "GIVEN_NAME":
            partes_nome.append(ent.text)
        elif ent.label_ == "SURNAME":
            partes_sobrenome.append(ent.text)

    return " ".join(partes_nome), " ".join(partes_sobrenome)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Separar nome e sobrenome usando modelo spaCy.\n"
            "Aceita um nome completo ou o caminho para um arquivo .csv com uma lista de nomes."
        )
    )
    parser.add_argument(
        "input",
        type=str,
        help=(
            "Nome completo (entre aspas) ou caminho para arquivo .csv contendo nomes completos."
        ),
    )

    args = parser.parse_args()

    modelo = carregar_modelo()

    entrada = args.input
    # Se for um arquivo csv existente, processa o arquivo
    if os.path.isfile(entrada) and entrada.lower().endswith(".csv"):
        csv_path = Path(entrada)
        saída_nome = csv_path.with_name(csv_path.stem + "_separado.csv")

        with csv_path.open("r", newline="", encoding="utf-8") as f_in:
            reader = csv.reader(f_in)
            rows = [r for r in reader if r and any(cell.strip() for cell in r)]

        resultados = []
        for r in rows:
            # assume first non-empty cell is o nome completo
            full = next((c for c in r if c and c.strip()), "").strip()
            primeiro, ultimo = separar_nome(modelo, full)
            resultados.append((full, primeiro, ultimo))

        # escreve arquivo de saída no mesmo diretório
        with saída_nome.open("w", newline="", encoding="utf-8") as f_out:
            writer = csv.writer(f_out)
            writer.writerow(["full_name", "first_name", "last_name"])
            for full, primeiro, ultimo in resultados:
                writer.writerow([full, primeiro, ultimo])

        print(f"Processado {len(resultados)} nomes.")
        print(f"Arquivo salvo em: {saída_nome}")
    else:
        # trata como um único nome
        nome, sobrenome = separar_nome(modelo, entrada)
        print(f"Entrada: {entrada}")
        print(f"Nome: {nome}")
        print(f"Sobrenome: {sobrenome}")


if __name__ == "__main__":
    main()
