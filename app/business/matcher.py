from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import csv
from sqlalchemy import * 
from orm_cim import ORM
from models import *

class Matcher():
    alphabet=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

    def __init__(self,model_path,path_emb,orm):
        self.model = SentenceTransformer(model_path)
        self.db_orm = orm

        #codes et descriptions à l'échelle de la CIM-X entière, ils doivent être rechargés avec la fonction reload_cim10
        self.codes=[]
        self.descriptions=[]
        self.embeddings=[]
        self.reload_cim10(path_emb)

    def reload_cim10(self,path_emb) :
        self.codes = orm.session.query(Code.cid).all() #faire une fonction orm.codes() -> plus de transparences sur la gestion du modèle
        self.descriptions = orm.session.query(Code.description).all() #idem avec description
        embeddings = [] #idem avec embeddings, ils doivent être géré par l'orm
        for letter in self.alphabet :
            NPYfile = 'code-'+letter+'.npy'
            pathEMB = path_emb / NPYfile
            embeddings.append(np.load(pathEMB))
        self.embeddings = np.concatenate(embeddings)
        return 

    ## ! à déplacer dans ORM ! ## 
    # def recompute_cim10(self, path_emb) :
    #     C=[]
    #     D=[]
    #     embeddings=[]
    #     for letter in alphabet :
    #         filename = 'code-'+letter+'.csv'
    #         path = current_dir.parent / "lib" / "CIM" / "code-csv" / filename
    #         with open(path, newline='\n') as csvfile:
    #             d2=[]
    #             reader = csv.reader(csvfile, delimiter=';', quotechar='"')
    #             for row in reader:
    #                 C.append(row[0])
    #                 D.append(row[1])
    #                 d2.append(row[1])
    #             d = model.encode(d2)
    #             embeddings.append(d)
    #             savefile = 'code-'+letter+'.npy'
    #             pathS = current_dir.parent / "lib" / "CIM" / "icd10NPY" / savefile
    #             np.save(pathS,d)
    #     embeddings2 = np.concatenate(embeddings)
    #     return C,D,embeddings2

    def match_cim10(self,bloc2_results):

        # Embedding des entités extraites par Bloc_2
        bloc2_embeddings = self.model.encode(bloc2_results)

        # Calcul des similarités cosinus entre les entités et les descriptions ICD-10
        similarities = cosine_similarity(bloc2_embeddings, self.embeddings)

        bloc3_results = []

        for i, entity in enumerate(bloc2_results):
            # Tri des indices par ordre décroissant de similarité
            best_match_indices = np.argsort(similarities[i])[::-1]

            # Récupération des trois meilleures correspondances
            best_match_index = best_match_indices[0]
            second_best_match_index = best_match_indices[1]
            third_best_match_index = best_match_indices[2]

            # Description et code ICD-10 correspondant
            best_icd10_description = self.descriptions[best_match_index]
            best_icd10_code = self.codes[best_match_index]
            second_best_icd10_description = self.codes[second_best_match_index]
            second_best_icd10_code = self.descriptions[second_best_match_index]
            third_best_icd10_description = self.codes[third_best_match_index]
            third_best_icd10_code = self.descriptions[third_best_match_index]

            # Stockage des résultats sous forme de dictionnaire
            bloc3_results.append({
                "entity": entity,
                "best_match_code": best_icd10_code,
                "best_match_description": best_icd10_description,
                "second_best_match_code": second_best_icd10_code,
                "second_best_match_description": second_best_icd10_description,
                "third_best_match_code": third_best_icd10_code,
                "third_best_match_description": third_best_icd10_description
            })

        return bloc3_results


if __name__ == "__main__":

    current_dir = Path(__file__).resolve().parent  # Obtenir le répertoire où le script est situé
    path_emb = current_dir.parent.parent/ "app-aime" / "lib" / "CIM" / "icd10NPY"
    orm = ORM("/test_cim.db")
    matcher = Matcher('FremyCompany/BioLORD-2023-M',path_emb,orm)
    print(matcher.codes)
    # Exemple d'utilisation
    bloc2_results = ["douleurs thoraciques"]
    results = matcher.match_cim10(bloc2_results)
    for result in results:
        print(result)