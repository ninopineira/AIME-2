from sentence_transformers import SentenceTransformer
import numpy as np
import time 
from chargement_code import chargement_txt, chargement_csv, chargement_numpy, export_numpy
import csv
import matplotlib.pyplot as plt

def tps_code_embedd() :
    [C,D] = np.load('testnumpy.npy')
    start = time.time()
    model = SentenceTransformer('FremyCompany/BioLORD-2023-M')
    icd10Embeded = model.encode(D)
    end = time.time()
    return (icd10Embeded, end-start)


def tps_alpha_embedd() :
    tps = []
    alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

    model = SentenceTransformer('FremyCompany/BioLORD-2023-M')
    icd10Embeded = []
    start = time.time()

    for letter in alphabet :
        path = './code-csv/code-'+letter+'.csv'
        with open(path, newline='\n') as csvfile:
            C=[]
            D=[]
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                C.append(row[0])
                D.append(row[1])
            icd10Embeded.append(model.encode(D))
            tps.append(time.time()-start)
            print(tps)

    plt.plot(alphabet,tps)
    plt.show()
    return

def schema_tps_sauvegarde() :
    tps = [11.20812177658081, 23.97739601135254, 38.15667366981506, 50.78426957130432, 62.95657658576965, 76.23838591575623, 89.32658982276917, 102.26475834846497, 117.55100297927856, 124.64215564727783, 138.64279341697693, 148.78798413276672, 165.19827270507812, 177.05582475662231, 191.1969780921936, 203.0900537967682, 221.95227074623108, 228.9365429878235, 250.8446352481842, 274.02675700187683, 275.5942075252533, 284.313196182251, 284.520681142807, 285.7943353652954, 286.4418704509735, 311.64455246925354]
    tps2 = [tps[0]]
    for i in range (1,len(tps)) :
        tps2.append(tps[i]-tps[i-1])
    alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    plt.plot(alphabet,tps,"r+",label="Temps cumulé")
    plt.plot(alphabet,tps2,"bo", label="Temps par famille de code")
    moy = np.mean(tps2)
    plt.plot([moy for _ in alphabet], 'g-', label =f"y={moy:.2f} s") # Red straight line
    plt.ylabel("temps (s)")
    plt.legend(loc='best')
    plt.show()
    return


schema_tps_sauvegarde()

#np.save("./icd10Embeded.npy",icd10Embeded)