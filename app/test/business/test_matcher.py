import pytest
import sys
from pathlib import Path

# Setup du path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent.parent.parent))

from app.src.business.matcher import Matcher
from app.src.models.orm_cim import ORM

# Configuration d'un "fixture" pytest pour initialiser le Matcher une seule fois
# et le réutiliser pour tous les tests (car charger le modèle prend plusieurs secondes)
@pytest.fixture(scope="module")
def matcher_instance():
    # Pour le test, on va chercher la vraie BDD applicative
    paths_src = current_dir.parent.parent / "src" / "data"
    pathDB = paths_src / "aime2-cim.db"
    pathEMB = paths_src / "aime2-embeddings.npy"
    
    # On vérifie que la BDD existe avant de lancer les tests
    if not pathDB.exists():
        pytest.skip("Base de données introuvable pour les tests.")
        
    orm = ORM(pathDB, pathEMB)
    return Matcher('FremyCompany/BioLORD-2023-M', orm)

def test_exact_match(matcher_instance):
    """Test qu'un terme exact renvoie bien le bon code CIM en premier choix."""
    bloc2_results = ["choléra"]
    res = matcher_instance.match_cim10(bloc2_results, threshold=0.8)
    
    assert len(res) == 1
    # Le choléra devrait idéalement pointer vers A00 (ou A00.9)
    assert res[0]["best_match_code"] is not None
    assert "A00" in res[0]["best_match_code"]

def test_below_threshold(matcher_instance):
    """Test qu'un mot complètement hors sujet ne trouve aucune correspondance via le seuil."""
    bloc2_results = ["tournevis"] # Aucune chance que ça soit dans la CIM !
    res = matcher_instance.match_cim10(bloc2_results, threshold=0.8) # Seuil strict
    
    assert len(res) == 1
    # Le match_code devrait être None car on a ignoré les résultats insatisfaisants
    assert res[0]["best_match_code"] is None
    assert "Aucune correspondance" in res[0]["best_match_description"]

def test_multiple_entities(matcher_instance):
    """Test le passage de multiples problèmes d'un seul coup."""
    bloc2_results = ["fièvre", "douleur au bras"]
    res = matcher_instance.match_cim10(bloc2_results, threshold=0.5) # Seuil permissif
    
    assert len(res) == 2
    # Le premier résultat doit correspondre à "fièvre"
    assert res[0]["entity"] == "fièvre"
    # Le second à "douleur au bras"
    assert res[1]["entity"] == "douleur au bras"
