import time
from chargement_code import chargement_ancien, chargement_csv, chargement_numpy

start = time.time()
chargement_ancien()
end = time.time()

print(f"Le temps de chargement nécessaire pour l'ancienne méthode est : %d",end-start)