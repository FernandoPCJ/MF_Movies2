from sqlmodel import SQLModel, Field

class ListaFilmeLink(SQLModel, table=True):
    lista_favoritos_id: int = Field(foreign_key="listafavoritos.id", primary_key=True)
    filme_id: int = Field(foreign_key="filme.id", primary_key=True)

