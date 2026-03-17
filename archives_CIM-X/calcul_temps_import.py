import time
from chargement_code import chargement_txt, chargement_csv, chargement_numpy, export_numpy
import matplotlib.pyplot as plt
import numpy as np

def petit_print() :
    start = time.time()
    chargement_txt()
    end = time.time()
    print("Le temps de chargement nécessaire pour l'ancienne méthode est :",end-start)

    alph_ancien = ["F","Z"]
    alph_etendu = ["E","I","J","K","F","X","Z"]
    alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

    start = time.time()
    chargement_csv(alph_ancien)
    end = time.time()
    print("Le temps de chargement nécessaire pour l'alphabet",alph_ancien,"est : ",end-start)

    start = time.time()
    chargement_csv(alph_etendu)
    end = time.time()
    print("Le temps de chargement nécessaire pour l'alphabet",alph_etendu,"est : ",end-start)

    start = time.time()
    chargement_csv(alphabet)
    end = time.time()
    print("Le temps de chargement nécessaire pour l'alphabet complet est : ",end-start)
    
    return

def temps_txt(N) :
    tps = []
    for i in range (0,N) :
        start = time.time()
        chargement_txt()
        end = time.time()
        tps.append(end-start)
    return tps

def temps_csv_alphabet(N,alphabet) :
    tps = []
    for i in range (0,N) :
        start = time.time()
        chargement_csv(alphabet)
        end = time.time()
        tps.append(end-start)
    return tps

def temps_npy_alphabet(N,alphabet) :
    (C,D) = chargement_csv(alphabet)
    export_numpy(C,D,'./testnumpy.npy')
    tps = []
    for i in range (0,N) :
        start = time.time()
        chargement_numpy('./testnumpy.npy')
        end = time.time()
        tps.append(end-start)
    return tps    

def print_graph(N = 100):
    alph_ancien = ["F","Z"]
    alph_etendu = ["E","I","J","K","F","X","Z"]
    alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

    tpstxt = temps_txt(N)
    tpsAancien = temps_csv_alphabet(N,alph_ancien)
    tpsAetendu = temps_csv_alphabet(N,alph_etendu)
    tpsAlphabet = temps_csv_alphabet(N,alphabet)
    tpsNpyAetendu = temps_npy_alphabet(N,alph_etendu)
    tpsNpyAlphabet = temps_npy_alphabet(N,alphabet)

    n = np.arange(0,N,1)

    plt.plot(n,tpstxt,'co',label="temps import txt (F,Z)")
    plt.plot(n,tpsAancien,'bo',label="temps import csv (F,Z)")
    plt.plot(n,tpsAetendu,'ro',label="temps import csv (E,F,I,J,K,X,Z)")
    plt.plot(n,tpsAlphabet,'go',label="temps import csv CIM-10")
    plt.plot(n,tpsNpyAetendu,'mo',label="temps import npy (E,F,I,J,K,X,Z)")
    plt.plot(n,tpsNpyAlphabet,'yo',label="temps import npy CIM-10")
    plt.legend(loc='best')
    plt.ylabel("temps (s)")
    plt.xlabel("iteration")
    plt.show()

def temps_npy_icd10(N) :
    tps = []
    for i in range (0,N) :
        start = time.time()
        L = np.load('./icd10Embeded.npy')
        end = time.time()
        tps.append(end-start)
    print(L)
    return tps  

def icd10npy() :
    N = 100
    tps = temps_npy_icd10(N)
    n = np.arange(0,N,1)
    plt.plot(n,tps,'bo',label="temps import npy CIM-10 vectorisée")
    moy = np.mean(tps)
    plt.plot([moy for _ in range (1,N+1)], 'r-', label =f"moyenne={moy:.4f} s") # Red straight line
    plt.legend(loc='best')
    plt.ylabel("temps (s)")
    plt.xlabel("iteration")
    plt.show()

print_graph()