from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from modelos.associacoes import ListaFilmeLink

if TYPE_CHECKING:
    from .lista_favoritos import ListaFavoritos
    from .avaliacao import Avaliacao

class Filme(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    diretor: str
    ano_lancamento: int
    sinopse: str
    duracao: int
    genero: str

    
    listas_favoritos: List["ListaFavoritos"] = Relationship(back_populates="filmes", link_model=ListaFilmeLink)
    avaliacoes: List["Avaliacao"] = Relationship(back_populates="filme")