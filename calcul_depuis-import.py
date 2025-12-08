import time
from chargement_code import chargement_txt, chargement_csv, chargement_numpy, export_numpy
import matplotlib.pyplot as plt
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('FremyCompany/BioLORD-2023-M')

icd10_embeddings = np.load("icd10Embeded.npy")

def match_cim10(bloc2_results):

    # Embedding des entités extraites par Bloc_2
    bloc2_embeddings = model.encode(bloc2_results)

    # Calcul des similarités cosinus entre les entités et les descriptions ICD-10
    similarities = cosine_similarity(bloc2_embeddings, icd10_embeddings)

    bloc3_results = []

    for i, entity in enumerate(bloc2_results):
        # Tri des indices par ordre décroissant de similarité
        best_match_indices = np.argsort(similarities[i])[::-1]

        # Récupération des trois meilleures correspondances
        best_match_index = best_match_indices[0]
        second_best_match_index = best_match_indices[1]
        third_best_match_index = best_match_indices[2]

        # Description et code ICD-10 correspondant
        best_icd10_description = D[best_match_index]
        best_icd10_code = C[best_match_index]
        second_best_icd10_description = D[second_best_match_index]
        second_best_icd10_code = C[second_best_match_index]
        third_best_icd10_description = D[third_best_match_index]
        third_best_icd10_code = C[third_best_match_index]

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
    # Exemple d'utilisation
    bloc2_results = ["douleurs thoraciques"]
    results = match_cim10(bloc2_results)
    for result in results:
        print(result)