from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .lista_favoritos import ListaFavoritos
    from .avaliacao import Avaliacao

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str

    listas_favoritos: List["ListaFavoritos"] = Relationship(back_populates="usuario")
    avaliacoes: List["Avaliacao"] = Relationship(back_populates="usuario")
