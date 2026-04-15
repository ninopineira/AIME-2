import pytest
import sys
from pathlib import Path

# Setup du path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent.parent.parent))

from app.src.business.paragraphe import extract_text

def test_extract_text_standard():
    """Test l'extraction avec toutes les sections présentes."""
    texte = """
    HISTOIRE DE LA MALADIE
    Le patient est arrivé hier.
    PRISE EN CHARGE SOMATIQUE
    Il a reçu un traitement.
    EXAMEN PSYCHIATRIQUE
    Tout va bien.
    MOTIF D'HOSPITALISATION
    Fièvre.
    ANTECEDENTS
    Rien à signaler.
    CONCLUSION
    Retour à domicile.
    BMR
    Négatif.
    """
    resultat = extract_text(texte)
    
    # On s'attend à 4 sections extraites
    assert len(resultat) == 4
    assert "Le patient est arrivé hier." in resultat[0]
    assert "Il a reçu un traitement." in resultat[1]
    assert "Fièvre." in resultat[2]
    assert "Retour à domicile." in resultat[3]

def test_extract_text_missing_sections():
    """Test l'extraction quand certaines sections sont manquantes."""
    texte = """
    HISTOIRE DE LA MALADIE
    Le patient est arrivé hier.
    PRISE EN CHARGE SOMATIQUE
    """
    resultat = extract_text(texte)
    
    # On s'attend à 1 seule section extraite (entre HISTOIRE et PRISE EN CHARGE)
    assert len(resultat) == 1
    assert "Le patient est arrivé hier." in resultat[0]

def test_extract_text_empty():
    """Test avec un texte vide ou ne contenant aucune section pertinente."""
    texte = "Bonjour, voici un texte sans rapport."
    resultat = extract_text(texte)
    
    assert isinstance(resultat, list)
    assert len(resultat) == 0

def test_extract_text_real_example():
    """Test avec un exemple plus proche de la vraie vie (tiré du main de paragraphe.py)."""
    texte = "MOTIF D'HOSPITALISATION : Hospitalisation ce jour pour sevrage 1 mois.\nANTECEDENTS PERSONNELS : Antécédents Psychiatriques...\nHISTOIRE DE LA MALADIE : Patient suivi habituellement en ambulatoire.\nPRISE EN CHARGE SOMATIQUE : RAS.\nEXAMEN PSYCHIATRIQUE : Normal.\nCONCLUSION : Sortie prévue.\nBMR : Négatif."
    resultat = extract_text(texte)
    
    # On a mis les 4 blocs
    assert len(resultat) == 4
    assert "Patient suivi habituellement en ambulatoire." in resultat[0]
    assert "RAS." in resultat[1]
    assert "Hospitalisation ce jour pour sevrage 1 mois." in resultat[2]
    assert "Sortie prévue." in resultat[3]
