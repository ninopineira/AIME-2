import numpy as np

def chargement_ancien() :
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

def chargement_csv():
    return 

def export_csv_numpy():
    return

def chargement_numpy():
    return
    
chargement_ancien()