from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from modelos.avaliacao import Avaliacao
from modelos.filme import Filme
from modelos.usuario import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("/", response_model=Usuario)
def criar_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    """
    Cria um novo usuário.
    """ 
    usuario_existente = session.get(Usuario, usuario.id)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="ID de usuário já utilizado")
    email_existente = session.exec(select(Usuario).where(Usuario.email == usuario.email)).first()
    if email_existente:
        raise HTTPException(status_code=400, detail="Endereço de e-mail já utilizado")
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/", response_model=List[Usuario])
def listar_usuarios(limit: int = 10, offset: int = 0, session: Session = Depends(get_session)):
    """
    Lista todos os usuários.
    """
    statement = select(Usuario).limit(limit).offset(offset)
    return session.exec(statement).all()


@router.get("/{usuario_id}", response_model=Usuario)
def obter_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """
    Retorna um usuário pelo ID.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.put("/{usuario_id}", response_model=Usuario)
def atualizar_usuario(usuario_id: int, usuario: Usuario, session: Session = Depends(get_session)):
    """
    Atualiza os dados de um usuário existente.
    """
    usuario_existente = session.get(Usuario, usuario_id)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario_existente.nome = usuario.nome
    usuario_existente.email = usuario.email
    session.commit()
    session.refresh(usuario_existente)
    return usuario_existente

@router.delete("/{usuario_id}")
def deletar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """
    Deleta um usuário pelo ID.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(usuario)
    session.commit()
    return {"detail": "Usuário deletado com sucesso"}

@router.get("/{usuario_id}/avaliacoes", response_model=List[dict])
def listar_avaliacoes_usuario(usuario_id: int, limit: int = 10, offset: int = 0, session: Session = Depends(get_session)):
    """
    Lista todas as avaliações de um usuário, incluindo o título do filme e o nome do usuário.
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    statement = (
    select(
            Avaliacao.id,
            Avaliacao.nota,
            Avaliacao.comentario,
            Filme.titulo.label("filme_titulo"),
            Usuario.nome.label("usuario_nome"),
        )
        .join(Filme, Filme.id == Avaliacao.filme_id)
        .join(Usuario, Usuario.id == Avaliacao.usuario_id)
        .where(Avaliacao.usuario_id == usuario_id)
        .limit(limit)
        .offset(offset)
    )
    resultados = session.exec(statement).all()

    return [
        {
            "id": avaliacao.id,
            "nota": avaliacao.nota,
            "comentario": avaliacao.comentario,
            "filme_titulo": avaliacao.filme_titulo,
            "usuario_nome": avaliacao.usuario_nome,
        }
        for avaliacao in resultados
    ]
