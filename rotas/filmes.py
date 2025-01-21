from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from database import get_session
from modelos.filme import Filme

router = APIRouter(prefix="/filmes", tags=["Filmes"])

@router.post("/", response_model=Filme)
def criar_filme(filme: Filme, session: Session = Depends(get_session)):
    """
    Cria um novo filme.
    """
    session.add(filme)
    session.commit()
    session.refresh(filme)
    return filme

# @router.get("/", response_model=list[Filme])
# def listar_filmes(
#     tituloContains: str | None = Query(None),
#     session: Session = Depends(get_session)
# ):
#     """
#     Retorna todos os filmes ou filtra por nome parcial no título.
#     """
#     query = select(Filme)
#     if tituloContains:
#         query = query.where(Filme.titulo.ilike(f"%{tituloContains}%"))
#     filmes = session.exec(query).all()
#     if not filmes:
#         raise HTTPException(status_code=404, detail="Nenhum filme encontrado com o título especificado")
#     return filmes
#   ***outra forma de fazer as consultas abaixo***

@router.get("/", response_model=List[Filme])
def listar_filmes(session: Session = Depends(get_session)):
    """
    Retorna todos os filmes.
    """
    filmes = session.exec(select(Filme)).all()
    if not filmes:
        raise HTTPException(status_code=404, detail="Nenhum filme encontrado.")
    return filmes

@router.get("/parcial", response_model=List[Filme])
def listar_filmes_parcial(
    tituloContains: str | None = Query(None),
    session: Session = Depends(get_session)
):
    """
    Retorna filmes filtrados por nome parcial no título.
    """
    if not tituloContains:
        raise HTTPException(status_code=400, detail="É obrigatório preencher o 'tituloContains' para esta consulta.")
    
    query = select(Filme).where(Filme.titulo.ilike(f"%{tituloContains}%"))
    filmes = session.exec(query).all()
    if not filmes:
        raise HTTPException(status_code=404, detail="Nenhum filme encontrado com o título especificado.")
    return filmes


@router.get("/{filme_id}", response_model=Filme)
def obter_filme(filme_id: int, session: Session = Depends(get_session)):
    """
    Retorna um filme pelo ID.
    """
    filme = session.get(Filme, filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    return filme

@router.put("/{filme_id}", response_model=Filme)
def atualizar_filme(filme_id: int, filme: Filme, session: Session = Depends(get_session)):
    """
    Atualiza os dados de um filme existente.
    """
    filme_existente = session.get(Filme, filme_id)
    if not filme_existente:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    
    filme_existente.titulo = filme.titulo
    filme_existente.diretor = filme.diretor
    filme_existente.ano_lancamento = filme.ano_lancamento
    filme_existente.sinopse = filme.sinopse
    filme_existente.duracao = filme.duracao
    filme_existente.generos = filme.genero
    session.commit()
    session.refresh(filme_existente)
    return filme_existente

@router.delete("/{filme_id}")
def deletar_filme(filme_id: int, session: Session = Depends(get_session)):
    """
    Deleta um filme pelo ID.
    """
    filme = session.get(Filme, filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    session.delete(filme)
    session.commit()
    return {"detail": "Filme deletado com sucesso"}

@router.get("/genero/{genero}", response_model=list[Filme])
def listar_filmes_por_genero(
    genero: str, session: Session = Depends(get_session)
):
    """
    Lista todos os filmes de um gênero específico.
    """
    filmes = session.exec(select(Filme).where(Filme.genero == genero)).all()

    if not filmes:
        raise HTTPException(
            status_code=404,
            detail=f"Não foram encontrados filmes para o gênero {genero}",
        )

    return filmes


@router.get("/diretor/{diretor}", response_model=list[Filme])
def listar_filmes_por_diretor(diretor: str, session: Session = Depends(get_session)):
    """
    Lista todos os filmes de um diretor específico.
    """
    filmes = session.exec(select(Filme).where(Filme.diretor == diretor)).all()

    if not filmes:
        raise HTTPException(
            status_code=404,
            detail=f"Não foram encontrados filmes dirigidos por '{diretor}'"
        )

    return filmes

@router.get("/ano-lancamento/{ano_lancamento}", response_model=list[Filme])
def listar_filmes_por_ano_lancamento(
    ano_lancamento: int,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """
    Retorna todos os filmes lançados em um ano específico.
    """
    query = select(Filme).where(Filme.ano_lancamento == ano_lancamento).offset(skip).limit(limit)
    filmes = session.exec(query).all()
    if not filmes:
        raise HTTPException(status_code=404, detail="Nenhum filme encontrado para o ano especificado")
    return filmes


@router.get("/ordem/ordenados-por-ano", response_model=list[Filme])
def listar_filmes_ordenados_por_ano(
    ordem: Literal["asc", "desc"] = "asc",
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """
    Retorna todos os filmes ordenados por ano de lançamento.
    """
    query = select(Filme).order_by(Filme.ano_lancamento.asc() if ordem == "asc" else Filme.ano_lancamento.desc())
    filmes = session.exec(query.offset(skip).limit(limit)).all()
    return filmes
