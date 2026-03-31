import pytest
import sys
from pathlib import Path

# Ajout du chemin parent pour pouvoir importer 'app'
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent.parent.parent))

from app.src.business.syntagme import extract_pathologies

def test_extract_simple_pathology():
    """Test l'extraction d'une pathologie simple sans négation."""
    texte = "Le patient présente une toux sèche sévère ce matin."
    resultats = extract_pathologies(texte)
    # Le modèle devrait au moins détecter la toux
    assert len(resultats) > 0
    assert any("toux" in res.lower() for res in resultats)

def test_extract_negation():
    """Test que la négation est bien prise en compte et qu'aucune pathologie n'est extraite."""
    texte = "Le patient n'a pas de fièvre ni de douleurs abdominales."
    resultats = extract_pathologies(texte)
    # Rien ne doit être extrait car tout est nié
    assert len(resultats) == 0

def test_extract_complex_sentence():
    """Test une phrase mixte avec une négation et une affirmation séparées par une conjonction."""
    texte = "Je n'ai pas de douleurs abdominales, mais je ressens des douleurs thoraciques."
    resultats = extract_pathologies(texte)
    
    # Doit contenir exactement 1 résultat (les douleurs thoraciques)
    assert len(resultats) == 1
    assert "douleurs thoraciques" in resultats[0].lower()
    # Ne doit PAS contenir de douleurs abdominales
    assert "abdominale" not in resultats[0].lower()

def test_no_medical_context():
    """Test avec une phrase sans aucun contexte médical."""
    texte = "Bonjour, je viens pour le rendez-vous de 15h."
    resultats = extract_pathologies(texte)
    assert len(resultats) == 0
