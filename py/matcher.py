import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import csv
import json
import math

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
        count = 0
        with open(pathCD, newline='\n', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                C.append(row[0])
                D.append(row[1])
                count += 1

        # Chargement des embeddings et s'assurer qu'on ne prend que ce qui correspond au CSV
        emb = np.load(pathEMB)
        if len(emb) > count:
            emb = emb[-count:] # On prend les derniers si cumulés indûment
        embeddings.append(emb)

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

def load_occurrences():
    """Charge les occurrences des codes médicaux depuis le fichier JSON."""
    path = current_dir.parent / "lib" / "CIM" / "occurrences.json"
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Seuil de similarité minimale pour accepter un code
#en dessous de 60% de similarité, on rejette le code
THRESHOLD = 0.6

def match_cim10(bloc2_results):

    # Embedding des entités extraites par Bloc_2
    bloc2_embeddings = model.encode(bloc2_results)

    # Calcul des similarités cosinus entre les entités et les descriptions ICD-10
    similarities = cosine_similarity(bloc2_embeddings, icd10_embeddings)

    # Récupération des occurrences pour la pondération
    occ_data = load_occurrences()
    max_occ = max(occ_data.values()) if occ_data else 1

    bloc3_results = []

    for i, entity in enumerate(bloc2_results):
        # Scores pour tous les codes
        scores = []
        for j, code in enumerate(C):
            sim = similarities[i][j]
            
            # Filtre par seuil
            if sim < THRESHOLD:
                continue
                
            # Calcul du poids lié à la fréquence (échelle logarithmique)
            occ = occ_data.get(code, 1) # 1 par défaut si inconnu

            #À quel point ce code est fréquent par rapport au code le plus fréquent, sur une échelle compressée
            freq_factor = math.log10(occ + 1) / math.log10(max_occ)
            
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
                "matches": []
            })
            continue

        # Récupération des meilleures correspondances
        matches = []
        for m_idx in range(min(3, len(scores))):
            idx = scores[m_idx]["index"]
            matches.append({
                "code": C[idx],
                "desc": D[idx]
            })

        # Stockage des résultats
        bloc3_results.append({
            "entity": entity,
            "matches": matches
        })

    return bloc3_results

# Utilisation du chemin relatif
model_path = Path(__file__).resolve().parent.parent / "models_cache" / "models--MiBo--SABERT"
# model = SentenceTransformer("distilbert/distilbert-base-multilingual-cased")
model = SentenceTransformer(model_path)



current_dir = Path(__file__).resolve().parent  # Obtenir le répertoire où le script est situé

## Block à décommenter pour une version "toute prête"
# embedded_path = current_dir.parent / "lib" / "CIM" / "icd10Embeded.npy"
# CD_path = current_dir.parent / "lib" / "CIM" / "testnumpy.npy"
# #charger une CIM-X déjà encoder
# icd10_embeddings = np.load(embedded_path)
# D = []  # Descriptions des codes ICD-10
# C = []  # Codes ICD-10
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