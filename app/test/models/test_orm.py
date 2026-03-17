# if __name__ == "__main__" :
import sys
from os.path import dirname, abspath
d = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(d)
from pathlib import Path
from src.models.orm_cim import ORM

## /!\ DISLCAIMER
# Le contenu n'a rien d'un fichier de test correct actuellement

current_dir = Path(__file__).resolve().parent
path_db = current_dir.parent / "data" / "test.db"
path_emb = current_dir.parent / "data" / "embeddings.npy"
print(str(path_db))
orm = ORM(path_db,path_emb)

# pathChapitre = current_dir.parent / "data" / "csv-BDD" / "chapitre.csv"
# pathGroupe   = current_dir.parent / "data" / "csv-BDD" / "groupe.csv"
# pathCode     = current_dir.parent / "data" / "csv-BDD" / "code.csv"
# # création de la table des chapitres depuis le csv donné
# orm.from_csv(pathChapitre,pathGroupe,pathCode)

# C = orm.codes()
# D = orm.codesDescription()

# for i in range (len(C)):
#     print(C[i]," : ",D[i])

emb = orm.embeddings()

print(emb[1:10])