from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .usuario import Usuario
    from .filme import Filme

class Avaliacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nota: int
    comentario: str

    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: "Usuario" = Relationship(back_populates="avaliacoes")

    filme_id: int = Field(foreign_key="filme.id")
    filme: "Filme" = Relationship(back_populates="avaliacoes")
