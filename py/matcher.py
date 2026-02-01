from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import csv

def reload_cim10(alphabet=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]) :
    C=[]
    D=[]
    embeddings = []
    for letter in alphabet :
        CSVfile = 'code-'+letter+'.csv'
        NPYfile = 'code-'+letter+'.npy'
        pathCD = current_dir.parent / "lib" / "CIM" / "code-csv" / CSVfile
        pathEMB = current_dir.parent / "lib" / "CIM" / "icd10NPY" / NPYfile
        # chargement Code et Description 
        with open(pathCD, newline='\n') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                C.append(row[0])
                D.append(row[1])

        
        embeddings.append(np.load(pathEMB))

    embeddings2 = np.concatenate(embeddings)

    return C,D,embeddings2

def recompute_cim10(alphabet=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]) :
    C=[]
    D=[]
    embeddings=[]
    for letter in alphabet :
        filename = 'code-'+letter+'.csv'
        path = current_dir.parent / "lib" / "CIM" / "code-csv" / filename
        with open(path, newline='\n') as csvfile:
            d2=[]
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                C.append(row[0])
                D.append(row[1])
                d2.append(row[1])
            d = model.encode(d2)
            embeddings.append(d)
            savefile = 'code-'+letter+'.npy'
            pathS = current_dir.parent / "lib" / "CIM" / "icd10NPY" / savefile
            np.save(pathS,d)
    embeddings2 = np.concatenate(embeddings)
    return C,D,embeddings2

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

# Utilisation du chemin relatif
#model_path = Path(__file__).resolve().parent.parent / "lib" / "models" / "BioLORD-2023-M"
# model = SentenceTransformer("distilbert/distilbert-base-multilingual-cased")
model = SentenceTransformer('FremyCompany/BioLORD-2023-M')

# D = []  # Descriptions des codes ICD-10
# C = []  # Codes ICD-10

current_dir = Path(__file__).resolve().parent  # Obtenir le répertoire où le script est situé

## Block à décommenter pour une version "toute prête"
# embedded_path = current_dir.parent / "lib" / "CIM" / "icd10Embeded.npy"
# CD_path = current_dir.parent / "lib" / "CIM" / "testnumpy.npy"
# #charger une CIM-X déjà encoder
# icd10_embeddings = np.load(embedded_path)
# [C,D] =  np.load(CD_path)

C,D,icd10_embeddings = reload_cim10()

## Si c'est la première execution :
# C,D,icd10_embeddings = recompute_cim10()

print(len(C),len(D),icd10_embeddings.shape)
if __name__ == "__main__":
    # print(icd10_embeddings)
    # Exemple d'utilisation
    bloc2_results = ["douleurs thoraciques"]
    results = match_cim10(bloc2_results)
    for result in results:
        print(result)