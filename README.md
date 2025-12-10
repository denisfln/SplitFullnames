# Separação de Nome e Sobrenome com spaCy

Este projeto utiliza um modelo de *Named Entity Recognition (NER)* treinado com spaCy para identificar automaticamente **nome** e **sobrenome** em nomes completos, considerando padrões brasileiros. É possível usar a solução via **API FastAPI** ou via **script local** no terminal.

---

## Executando a API

1. Instale as dependências:
```bash
pip install fastapi uvicorn[standard] spacy
```
2. Execute a API:
```bash
uvicorn api:app --reload
```
3. Instale as dependências:
```bash
curl -X POST -H "Content-Type: application/json" \
     -d "{\"nome_completo\": \"João Pedro da Silva\"}" \
     http://localhost:8000/separar
```

## Executando via Script Local

Execute o script passando o nome completo:
```bash
python separar_nome.py "Maria Aparecida de Souza"
```