from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from database import get_session
from modelos.associacoes import ListaFilmeLink
from modelos.filme import Filme
from modelos.lista_favoritos import ListaFavoritos
from modelos.usuario import Usuario

router = APIRouter(prefix="/listas-favoritos", tags=["Listas de Favoritos"])

@router.post("/", response_model=ListaFavoritos)
def criar_lista(lista: ListaFavoritos, session: Session = Depends(get_session)):
    """
    Cria uma nova lista de favoritos.
    """
    
    lista_existente = session.get(ListaFavoritos, lista.id)
    if lista_existente:
        raise HTTPException(status_code=400, detail="ID da lista já está em uso.")
    usuario_existente = session.get(Usuario, lista.usuario_id)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    session.add(lista)
    session.commit()
    session.refresh(lista)
    return lista

@router.get("/", response_model=list[ListaFavoritos])
def listar_listas(session: Session = Depends(get_session)):
    """
    Retorna todas as listas de favoritos.
    """
    return session.exec(select(ListaFavoritos)).all()

@router.get("/{lista_id}", response_model=ListaFavoritos)
def obter_lista(lista_id: int, session: Session = Depends(get_session)):
    """
    Retorna uma lista de favoritos pelo ID.
    """
    lista = session.get(ListaFavoritos, lista_id)
    if not lista:
        raise HTTPException(status_code=404, detail="Lista de favoritos não encontrada")
    return lista

@router.put("/{lista_id}", response_model=ListaFavoritos)
def atualizar_lista(lista_id: int, lista: ListaFavoritos, session: Session = Depends(get_session)):
    """
    Atualiza os dados de uma lista de favoritos existente.
    """
    lista_existente = session.get(ListaFavoritos, lista_id)
    if not lista_existente:
        raise HTTPException(status_code=404, detail="Lista de favoritos não encontrada")
    lista_existente.nome = lista.nome
    session.commit()
    session.refresh(lista_existente)
    return lista_existente

@router.delete("/{lista_id}")
def deletar_lista(lista_id: int, session: Session = Depends(get_session)):
    """
    Deleta uma lista de favoritos pelo ID.
    """
    lista = session.get(ListaFavoritos, lista_id)
    if not lista:
        raise HTTPException(status_code=404, detail="Lista de favoritos não encontrada")
    session.delete(lista)
    session.commit()
    return {"detail": "Lista de favoritos deletada com sucesso"}


@router.post("/{lista_id}/filmes/{filme_id}")
def adicionar_filme_lista(lista_id: int, filme_id: int, session: Session = Depends(get_session)):
    """
    Adiciona um filme à lista de favoritos.
    """
    lista_favoritos = session.get(ListaFavoritos, lista_id)
    if not lista_favoritos:
        raise HTTPException(status_code=404, detail="Lista de favoritos não encontrada.")

    filme = session.get(Filme, filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    filme_na_lista = session.get(ListaFilmeLink, (lista_id, filme_id))
    if filme_na_lista:
        raise HTTPException(status_code=400, detail="Filme já está na lista de favoritos.")

    novo_link = ListaFilmeLink(lista_favoritos_id=lista_id, filme_id=filme_id)
    session.add(novo_link)
    session.commit()
    session.refresh(novo_link)

    return {"message": "Filme adicionado à lista com sucesso!", "lista_id": lista_id, "filme_id": filme_id}


@router.delete("/{lista_id}/filmes/{filme_id}")
def remover_filme_lista(lista_id: int, filme_id: int, session: Session = Depends(get_session)):
    """
    Remove um filme da lista de favoritos.
    """
    lista_favoritos = session.get(ListaFavoritos, lista_id)
    if not lista_favoritos:
        raise HTTPException(status_code=404, detail="Lista de favoritos não encontrada.")

    filme = session.get(Filme, filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    filme_na_lista = session.get(ListaFilmeLink, (lista_id, filme_id))
    if not filme_na_lista:
        raise HTTPException(status_code=404, detail="O filme não está na lista de favoritos.")

    session.delete(filme_na_lista)
    session.commit()

    return {"message": "Filme removido da lista com sucesso!", "lista_id": lista_id, "filme_id": filme_id}

@router.get("/{lista_id}/filmes", response_model=list[Filme])
def listar_filmes_lista(lista_id: int, limit: int = 10, offset: int = 0, session: Session = Depends(get_session)):
    """
    Lista todos os filmes de uma lista de favoritos com paginação.
    """
    lista_favoritos = session.get(ListaFavoritos, lista_id)
    if not lista_favoritos:
        raise HTTPException(status_code=404, detail="Lista de favoritos não encontrada.")

    statement = (
        select(Filme)
        .join(ListaFilmeLink, ListaFilmeLink.filme_id == Filme.id)
        .where(ListaFilmeLink.lista_favoritos_id == lista_id)
        .limit(limit)
        .offset(offset)
    )
    filmes = session.exec(statement).all()
    return filmes

@router.get("/{lista_id}/filme/count", response_model=dict)
def contar_filmes_lista(lista_id: int, session: Session = Depends(get_session)):
    """
    Conta os filmes em uma lista de favoritos.
    """
    lista_favoritos = session.get(ListaFavoritos, lista_id)
    if not lista_favoritos:
        raise HTTPException(status_code=404, detail="Lista de favoritos não encontrada.")

    statement = select(func.count(ListaFilmeLink.filme_id)).where(ListaFilmeLink.lista_favoritos_id == lista_id)
    resultados = session.exec(statement).all()  
    total_filmes = session.exec(statement).first() or 0
    return {"lista_id": lista_id, "total_filmes": total_filmes}