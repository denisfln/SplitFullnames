import asyncio
import logging
from typing import List
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import spacy
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware


# -----------------------------------------------------
# Logging estruturado
# -----------------------------------------------------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Modelos de entrada e saída (Pydantic)
# -----------------------------------------------------
class SepararNomeInput(BaseModel):
    nome_completo: str

    @field_validator("nome_completo")
    def validar_nome(cls, value: str):
        if len(value.strip()) < 2:
            raise ValueError("O nome informado é muito curto.")
        if any(char.isdigit() for char in value):
            raise ValueError("O nome não pode conter números.")
        return value.strip()


class SepararNomeOutput(BaseModel):
    entrada: str
    nome: str
    sobrenome: str


# -----------------------------------------------------
# Inicialização do FastAPI
# -----------------------------------------------------
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],   # restrinja se necessário
        allow_methods=["GET"],
        allow_headers=["*"],
    )
]

app = FastAPI(
    title="API de Separação de Nome/Sobrenome",
    version="2.0.0",
    middleware=middleware
)


# -----------------------------------------------------
# Carregamento do modelo spaCy na inicialização
# -----------------------------------------------------
@app.on_event("startup")
async def carregar_modelo():
    global nlp
    try:
        logger.info("Carregando modelo spaCy...")
        nlp = spacy.load("./modelo_nomes/model-best")
        logger.info("Modelo carregado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {e}")
        raise RuntimeError("Falha ao iniciar o modelo spaCy.") from e


# -----------------------------------------------------
# Função de separação com timeout
# -----------------------------------------------------
async def executar_com_timeout(func, arg, timeout=3.0):
    try:
        return await asyncio.wait_for(asyncio.to_thread(func, arg), timeout)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Tempo limite excedido ao processar o nome."
        )


def separar_nome_logica(nome_completo: str):
    doc = nlp(nome_completo)

    nome: List[str] = []
    sobrenome: List[str] = []

    for ent in doc.ents:
        if ent.label_ == "GIVEN_NAME":
            nome.append(ent.text)
        elif ent.label_ == "SURNAME":
            sobrenome.append(ent.text)

    return " ".join(nome), " ".join(sobrenome)


# -----------------------------------------------------
# Endpoint principal
# -----------------------------------------------------
@app.post("/separar", response_model=SepararNomeOutput)
async def separar_nome(payload: SepararNomeInput):
    nome_completo = payload.nome_completo

    logger.info(f"Processando nome: {nome_completo}")

    try:
        nome, sobrenome = await executar_com_timeout(
            separar_nome_logica,
            nome_completo,
            timeout=3.0
        )

        if not nome and not sobrenome:
            raise HTTPException(
                status_code=422,
                detail="Não foi possível identificar nome e sobrenome."
            )

        return SepararNomeOutput(
            entrada=nome_completo,
            nome=nome,
            sobrenome=sobrenome
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar o nome."
        )


# -----------------------------------------------------
# Tratamento global de exceções
# -----------------------------------------------------
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro inesperado: {exc}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno não tratado."},
    )
