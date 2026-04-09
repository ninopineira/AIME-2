# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#from typing import Optional
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker , Session
from sqlalchemy.ext.declarative import declarative_base
from sentence_transformers import SentenceTransformer
import numpy as np 
import csv
from pathlib import Path
if __name__ == "__main__" :
    from models import Base, Groupe, Code, Chapitre
else :
    from .models import Base, Groupe, Code, Chapitre

class ORM():
    # db = SQLAlchemy(model_class=Base)
    db = Base
    engine = None #TEST : il faut vérifier ds les autres fction que ce n'est pas non lors de l'execution

    def __init__(self,path_db,path_emb):
        self.path_db = path_db
        self.path_emb = path_emb
        engine_path = "sqlite:///"+str(self.path_db)
        self.engine = create_engine(engine_path, echo=True)
        self.db.metadata.bind = self.engine
        self.session = scoped_session(sessionmaker())(bind=self.engine)
        # Base.metadata.create_all(self.engine)
        # self.DBSession = sessionmaker(bind=self.engine)
        # self.session = self.DBSession()

    
    def tableDrop(self) :
        self.db.metadata.drop_all(bind=self.engine)
        return

    def tableCreate(self):# Recréation des tables
        self.db.metadata.create_all(bind=self.engine)
        return 

    ## "setter"
    def recompute_cim10(self,model_path) :
        model = SentenceTransformer(model_path) 
        descriptions = self.codesDescription()
        embeddings = model.encode(descriptions)
        np.save(self.path_emb,embeddings)
        return embeddings

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
            with open(path, newline='\n',encoding='utf-8-sig') as csvfile:
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
        self.tableDrop()
        self.tableCreate()
        self.code_from_csv(pathCode)
        self.groupe_from_csv(pathGroupe)
        self.chapitre_from_csv(pathChapitre)

    def reload_codes(self, path):
        """Supprime tous les codes et les réimporte depuis un nouveau CSV."""
        with Session(self.engine) as session:
            session.query(Code).delete()
            session.commit()
        self.code_from_csv(path)
    
    ## "getter"
    def codes(self):
        codes = self.session.query(Code.cid).all()
        values = []
        for i in range (len(codes)) :
            values.append(codes[i][0])
        return values
    
    def codesDescription(self):
        description = self.session.query(Code.description).all()
        values = []
        for i in range (len(description)) :
            values.append(description[i][0])
        return values
    
    def embeddings(self):
        return np.load(self.path_emb)

if __name__ == "__main__":
    
    #chemin vers le script 
    current_dir = Path(__file__).resolve().parent
    pathDB = current_dir.parent / "data" / "aime2-cim.db"
    pathEMB = current_dir.parent / "data" / "aime2-embeddings"
    orm = ORM(pathDB,pathEMB)
    #chemin vers csv des chapitres
    pathChapitre = current_dir.parent / "data" / "csv-BDD" / "chapitre.csv"
    pathGroupe   = current_dir.parent / "data" / "csv-BDD" / "groupe.csv"
    pathCode     = current_dir.parent / "data" / "csv-BDD" / "code.csv"
    # création des tables depuis les csv donné
    # orm.from_csv(pathChapitre,pathGroupe,pathCode)
    orm.recompute_cim10('FremyCompany/BioLORD-2023-M')
