# __package__ = "app"
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import csv
from sqlalchemy import * 
if __name__ == "__main__" :
    import sys
    from os.path import dirname, abspath
    d = dirname(dirname(abspath(__file__)))
    sys.path.append(d)
    from models.orm_cim import ORM
    from models.models import *
else :
    from ..models.orm_cim import ORM
    from ..models.models import *

class Matcher():
    def __init__(self,model_path,orm):
        self.model = SentenceTransformer(model_path)
        self.db_orm = orm
        #codes et descriptions à l'échelle de la CIM-X entière, ils doivent être rechargés avec la fonction reload_cim10
        self.codes = orm.codes()
        self.descriptions = orm.codesDescription()
        self.embeddings = orm.embeddings()

    def reload_cim10(self):
        """Recharge en mémoire les codes, descriptions et embeddings depuis l'ORM."""
        self.codes = self.db_orm.codes()
        self.descriptions = self.db_orm.codesDescription()
        self.embeddings = self.db_orm.embeddings()

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
            second_best_icd10_description = self.descriptions[second_best_match_index]
            second_best_icd10_code = self.codes[second_best_match_index]
            third_best_icd10_description = self.descriptions[third_best_match_index]
            third_best_icd10_code = self.codes[third_best_match_index]

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
    pathDB = current_dir.parent / "data" / "aime2-cim.db"
    pathEMB = current_dir.parent / "data" / "aime2-embeddings.npy"
    orm = ORM(pathDB,pathEMB)
    matcher = Matcher('FremyCompany/BioLORD-2023-M',orm)
    # Exemple d'utilisation
    bloc2_results = ["douleurs thoraciques"]
    results = matcher.match_cim10(bloc2_results)
    for result in results:
        print(result)