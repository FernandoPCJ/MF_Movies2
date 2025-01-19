from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func
from database import get_session
from modelos.avaliacao import Avaliacao
from modelos.filme import Filme
from modelos.usuario import Usuario

router = APIRouter(prefix="/avaliacoes", tags=["Avaliações"])

@router.post("/", response_model=Avaliacao)
def criar_avaliacao(avaliacao: Avaliacao, session: Session = Depends(get_session)):
    """
    Cria uma nova avaliação para um filme, verificando se o usuário já avaliou o filme.
    """
    # Verifica se o usuário existe
    usuario = session.get(Usuario, avaliacao.usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # Verifica se o filme existe
    filme = session.get(Filme, avaliacao.filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    # Verifica se o usuário já avaliou o filme
    statement = select(Avaliacao).where(
        (Avaliacao.usuario_id == avaliacao.usuario_id) &
        (Avaliacao.filme_id == avaliacao.filme_id)
    )
    avaliacao_existente = session.exec(statement).first()
    if avaliacao_existente:
        raise HTTPException(
            status_code=400,
            detail="O usuário já realizou uma avaliação para este filme."
        )

    # Cria a nova avaliação
    session.add(avaliacao)
    session.commit()
    session.refresh(avaliacao)

    return avaliacao

@router.get("/", response_model=list[Avaliacao])
def listar_avaliacoes(session: Session = Depends(get_session)):
    """
    Retorna todas as avaliações.
    """
    return session.exec(select(Avaliacao)).all()

@router.get("/{avaliacao_id}", response_model=Avaliacao)
def obter_avaliacao(avaliacao_id: int, session: Session = Depends(get_session)):
    """
    Retorna uma avaliação pelo ID.
    """
    avaliacao = session.get(Avaliacao, avaliacao_id)
    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return avaliacao

@router.put("/{avaliacao_id}", response_model=Avaliacao)
def atualizar_avaliacao(avaliacao_id: int, avaliacao: Avaliacao, session: Session = Depends(get_session)):
    """
    Atualiza os dados de uma avaliação existente.
    """
    avaliacao_existente = session.get(Avaliacao, avaliacao_id)
    if not avaliacao_existente:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    
    avaliacao_existente.nota = avaliacao.nota
    avaliacao_existente.comentario = avaliacao.comentario
    avaliacao_existente.usuario_id = avaliacao.usuario_id
    avaliacao_existente.filme_id = avaliacao.filme_id
    session.commit()
    session.refresh(avaliacao_existente)
    return avaliacao_existente

@router.delete("/{avaliacao_id}")
def deletar_avaliacao(avaliacao_id: int, session: Session = Depends(get_session)):
    """
    Deleta uma avaliação pelo ID.
    """
    avaliacao = session.get(Avaliacao, avaliacao_id)
    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    session.delete(avaliacao)
    session.commit()
    return {"detail": "Avaliação deletada com sucesso"}

@router.get("/filmes/{filme_id}/avaliacoes", response_model=List[dict])
def listar_avaliacoes_filme(filme_id: int, session: Session = Depends(get_session)):
    """
    Lista todas as avaliações de um filme, incluindo o nome do usuário que avaliou.
    """
    # Verifica se o filme existe
    filme = session.get(Filme, filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    # Consulta para buscar avaliações do filme com o nome do usuário
    statement = (
        select(
            Avaliacao.id,
            Avaliacao.nota,
            Avaliacao.comentario,
            Usuario.nome.label("usuario_nome")
        )
        .join(Usuario, Usuario.id == Avaliacao.usuario_id)
        .where(Avaliacao.filme_id == filme_id)
    )
    resultados = session.exec(statement).all()

    # Retorna os resultados formatados
    return [
        {
            "id": avaliacao.id,
            "nota": avaliacao.nota,
            "comentario": avaliacao.comentario,
            "usuario_nome": avaliacao.usuario_nome,
        }
        for avaliacao in resultados
    ]

@router.get("/filmes/{filme_id}/media", response_model=dict)
def obter_media_notas_filme(filme_id: int, session: Session = Depends(get_session)):
    """
    Obtém a média de notas de um filme específico.
    """
    # Verifica se o filme existe
    filme = session.get(Filme, filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    # Consulta para calcular a média de notas
    statement = select(func.avg(Avaliacao.nota)).where(Avaliacao.filme_id == filme_id)
    resultados = session.exec(statement).all()  # Retorna uma lista com um único valor

    # Verifica se há resultados
    media = resultados[0] if resultados else None

    if media is None:
        raise HTTPException(status_code=404, detail="Nenhuma avaliação encontrada para este filme.")

    # Retorna a média arredondada
    return {"filme_id": filme_id, "media": round(media, 2)}
