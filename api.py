from fastapi import FastAPI
import spacy

app = FastAPI()
nlp = spacy.load("./modelo_nomes/model-best")

@app.get("/separar")
def separar(nome_completo: str):
    doc = nlp(nome_completo)
    nome = []
    sobrenome = []

    for ent in doc.ents:
        if ent.label_ == "GIVEN_NAME":
            nome.append(ent.text)
        elif ent.label_ == "SURNAME":
            sobrenome.append(ent.text)

    return {
        "entrada": nome_completo,
        "nome": " ".join(nome),
        "sobrenome": " ".join(sobrenome)
    }
