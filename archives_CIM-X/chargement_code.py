import numpy as np
import csv

def chargement_txt() :
    D = []  # Descriptions des codes ICD-10
    C = []  # Codes ICD-10
    #current_dir = Path(__file__).resolve().parent  # Obtenir le répertoire où le script est situé
    descriptions_path = "descriptions.txt"
    codes_path = "codes.txt"

    # Charger les fichiers contenant les descriptions et les codes ICD-10
    with open(descriptions_path, 'r', encoding='utf-8') as fichier:
        for ligne in fichier:
            D.append(ligne.strip())  # Ajouter chaque ligne comme une description

    with open(codes_path, 'r', encoding='utf-8') as fichier:
        for ligne in fichier:
            C.append(ligne.strip())  # Ajouter chaque ligne comme un code
    return (C,D)

def chargement_csv(alphabet):
    D = []  # Descriptions des codes ICD-10
    C = []  # Codes ICD-10

    for letter in alphabet :
        path = './code-csv/code-'+letter+'.csv'
        with open(path, newline='\n') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                C.append(row[0])
                D.append(row[1])
    return (C,D)

def export_numpy(C,D,path):
    icd10 = np.array([C,D])
    np.save(path,icd10)    
    return

def chargement_numpy(path):
    [C,D] = np.load(path)
    return (C,D)
    
