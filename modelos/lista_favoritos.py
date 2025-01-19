from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from modelos.associacoes import ListaFilmeLink

if TYPE_CHECKING:
    from .usuario import Usuario
    from .filme import Filme

class ListaFavoritos(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: "Usuario" = Relationship(back_populates="listas_favoritos")
    filmes: List["Filme"] = Relationship(back_populates="listas_favoritos", link_model=ListaFilmeLink)