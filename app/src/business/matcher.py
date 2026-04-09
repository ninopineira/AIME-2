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

    def load_occurrences(self):
        """Charge les occurrences des codes médicaux depuis le fichier JSON."""
        path = Path(__file__).resolve().parent.parent.parent.parent / "lib" / "CIM" / "occurrences.json"
        if path.exists():
            import json
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def match_cim10(self, bloc2_results, threshold=0.75):
        import math

        # Embedding des entités extraites par Bloc_2
        bloc2_embeddings = self.model.encode(bloc2_results)

        # Calcul des similarités cosinus entre les entités et les descriptions ICD-10
        similarities = cosine_similarity(bloc2_embeddings, self.embeddings)

        # Récupération des occurrences pour la pondération
        occ_data = self.load_occurrences()
        max_occ = max(occ_data.values()) if occ_data else 1

        bloc3_results = []

        for i, entity in enumerate(bloc2_results):
            # Scores pour tous les codes
            scores = []
            for j, code in enumerate(self.codes):
                sim = similarities[i][j]

                # Filtre par seuil
                if sim < threshold:
                    continue

                # Calcul du poids lié à la fréquence (échelle logarithmique)
                occ = occ_data.get(code, 1) # 1 par défaut si inconnu

                #À quel point ce code est fréquent par rapport au code le plus fréquent, sur une échelle compressée
                freq_factor = math.log10(occ + 1) / math.log10(max_occ) if max_occ > 1 else 1.0

                # Score final hybridé
                #2 citères pour un meilleur matching dans notre cas: cos similarity et fréquence d'occurence
                weighted_score = sim * freq_factor
                scores.append({
                    "index": j,
                    "sim": sim,
                    "weighted_score": weighted_score
                })

            # Tri par score pondéré décroissant
            scores.sort(key=lambda x: x["weighted_score"], reverse=True)

            if not scores:
                # Aucun code ne dépasse le seuil
                bloc3_results.append({
                    "entity": entity,
                    "best_match_code": None,
                    "best_match_description": "Aucune correspondance trouvée au dessus du seuil",
                    "second_best_match_code": None,
                    "second_best_match_description": "",
                    "third_best_match_code": None,
                    "third_best_match_description": ""
                })
                continue

            # Récupération des meilleures correspondances en gardant la structure originale attendue par app.py
            result_dict = {"entity": entity}

            prefixes = ["best_", "second_best_", "third_best_"]
            for m_idx in range(3):
                if m_idx < len(scores):
                    idx = scores[m_idx]["index"]
                    result_dict[f"{prefixes[m_idx]}match_code"] = self.codes[idx]
                    result_dict[f"{prefixes[m_idx]}match_description"] = self.descriptions[idx]
                else:
                    result_dict[f"{prefixes[m_idx]}match_code"] = None
                    result_dict[f"{prefixes[m_idx]}match_description"] = ""

            # Stockage des résultats
            bloc3_results.append(result_dict)

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
