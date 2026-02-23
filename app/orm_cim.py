from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from typing import Optional
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker , DeclarativeBase, Mapped, mapped_column, Session
import csv
from pathlib import Path
from models import Base, Groupe, Code, Chapitre

class ORM():
    db = SQLAlchemy(model_class=Base)
    engine = None #TEST : il faut vérifier ds les autres fction que ce n'est pas non lors de l'execution

    def __init__(self,path):
        self.engine = create_engine("sqlite://"+path, echo=True)
        Base.metadata.create_all(self.engine)
        self.DBSession = sessionmaker(bind=self.engine)
        self.session = self.DBSession()
    
    def clear_db(self):
        #ne marche que dans un contexte d'application : à voir
        self.db.drop_all()

    def chapitre_from_csv(self, path,chid=0,des=1):
        """
        path : chemin vers le CSV
        chid,des : colonnes du CSV dans lesquelles sont les informations
        """
        with Session(self.engine) as session :
            #il y a un caractère bizarre que je n'arrive pas à supprimer au début du csv des chapitres, donc on utilise l'encodage  encoding='utf-8-sig'
            with open(path, newline='\n',encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile,delimiter=';', quotechar='"')
                for row in reader:
                    session.add(Chapitre(chid=int(row[chid]),description=row[des]))
                session.commit()
    
    def groupe_from_csv(self,path,gid=0,chid=2,fin=1,des=3):
        """
        path : chemin vers le CSV
        gid,chid,fin,des : colonnes du CSV dans lesquelles sont les informations
        """
        with Session(self.engine) as session :
            with open(path, newline='\n') as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for row in reader:
                    session.add(Groupe(gid=row[gid],chid=int(row[chid]),fin=row[fin],description=row[des]))
                session.commit()

    def code_from_csv(self,path,cid=6,gid=4,des=8):
        """
        path : chemin vers le CSV
        cid,gid,des : colonnes du CSV dans lesquelles sont les informations
        """
        with Session(self.engine) as session :
            with open(path, newline='\n') as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for row in reader:
                    session.add(Code(cid=row[cid],gid=row[gid],c3c=row[cid][0:3],description=row[des]))
                session.commit()
    
    def from_csv(self,pathChapitre,pathGroupe,pathCode):
        """
        Ne peut être utilisée que si toutes les valeurs de colonnes par defaut correspondent aux valeurs préenregistrées
        """
        self.code_from_csv(pathCode)
        self.groupe_from_csv(pathGroupe)
        self.chapitre_from_csv(pathChapitre)

if __name__ == "__main__":
    #création de l'object relation mapping
    orm = ORM("/test_cim.db")
    
    #chemin vers le script 
    current_dir = Path(__file__).resolve().parent
    #chemin vers csv des chapitres
    pathChapitre = current_dir.parent / "lib" / "CIM" / "csv-BDD" / "chapitre.csv"
    pathGroupe   = current_dir.parent / "lib" / "CIM" / "csv-BDD" / "groupe.csv"
    pathCode     = current_dir.parent / "lib" / "CIM" / "csv-BDD" / "code.csv"

    # création de la table des chapitres depuis le csv donné
    # orm.clear_db()
    # orm.from_csv(pathChapitre,pathGroupe,pathCode)