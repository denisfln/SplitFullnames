import argparse
import spacy

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
    parser = argparse.ArgumentParser(description="Separar nome e sobrenome usando modelo spaCy.")
    parser.add_argument("nome_completo", type=str, help="Nome completo para processar.")

    args = parser.parse_args()

    modelo = carregar_modelo()
    nome, sobrenome = separar_nome(modelo, args.nome_completo)

    print(f"Entrada: {args.nome_completo}")
    print(f"Nome: {nome}")
    print(f"Sobrenome: {sobrenome}")


if __name__ == "__main__":
    main()
