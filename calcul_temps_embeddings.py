from sentence_transformers import SentenceTransformer
import numpy as np
import time 
from chargement_code import chargement_txt, chargement_csv, chargement_numpy, export_numpy

def tps_code_embedd() :
    [C,D] = np.load('testnumpy.npy')
    start = time.time()
    model = SentenceTransformer('FremyCompany/BioLORD-2023-M')
    icd10Embeded = model.encode(D)
    end = time.time()
    return (icd10Embeded, end-start)

icd10Embeded, time = tps_code_embedd()

np.save("./icd10Embeded.npy",icd10Embeded)