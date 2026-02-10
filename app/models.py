from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from typing import Optional
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import csv
from pathlib import Path

#equiv : Base = declarative_base()
class Base(DeclarativeBase):
  pass

class Chapitre(Base):
    __tablename__ = "chapitres"

    chid : Mapped[int] = mapped_column(primary_key=True)
    description : Mapped[str]

    groupes = relationship("Goupe",back_populates="chapitres")

    def __repr__(self) -> str:
        return f"Chapitre(cid={self.chid!r}, description='{self.description!r}')"  

class Groupe(Base):
    __tablename__ = "groupes"

    gid : Mapped[str] = mapped_column(primary_key=True)
    chid : Mapped[int] = mapped_column(ForeignKey("chapitres.chid"))
    #deb : Mapped[str] = mapped_column(str(3)) #redondant == gid
    fin : Mapped[str]
    description : Mapped[str]

    chapitres = relationship("Chapitre",back_populates="groupes")
    codes = relationship("Code",back_populates="groupes")

    def __repr__(self) -> str :
        return f"Groupe(gid={self.gid!r}, chid={self.chid!r}, fin={self.fin!r}, description='{self.description!r}')"

class Code(Base):
    __tablename__ = "codes"

    cid : Mapped[str] = mapped_column(primary_key=True)
    gid : Mapped[str] = mapped_column(ForeignKey("groupes.gid"))
    c3c : Mapped[str]
    description : Mapped[str]

    groupes = relationship("Groupe",back_populates="codes")

    def __repr__(self) -> str :
        return f"Code(gid={self.gid!r}, c3c={self.c3c!r}, cid={self.cid!r}, description='{self.description!r}')"

