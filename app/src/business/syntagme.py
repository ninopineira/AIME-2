from pathlib import Path
from medkit.core.text import TextDocument
from medkit.text.segmentation import SentenceTokenizer
from medkit.text.segmentation import SyntagmaTokenizer
from medkit.text.ner.hf_entity_matcher import HFEntityMatcher
from medkit.text.context import NegationDetector, NegationDetectorRule
from medkit.text.ner import RegexpMatcher, RegexpMatcherRule

def extract_pathologies(texte):

    #importation du texte
    doc = TextDocument(text=texte)

    #initialisation du tokenizer de phrases
    sent_tokenizer = SentenceTokenizer(
        output_label="sentence",
        punct_chars=[".", "?", "!"],
    )

    #segmentation du texte en phrases
    sentences = sent_tokenizer.run([doc.raw_segment])


    #initialisation du tokenizer de syntagmes
    synt_tokenizer = SyntagmaTokenizer(
        output_label="syntagma",
        separators=[r"\bmais\b", r"\bet\b"],
    )

    #segmentation des phrases en syntagmes
    syntagmas = synt_tokenizer.run(sentences)

    #Détection des négations

    #initialisation des règles de détection
    neg_rules = [
        NegationDetectorRule(regexp=r"\bpas\s*d[' e]\b"),
        NegationDetectorRule(regexp=r"\bsans\b", exclusion_regexps=[r"\bsans\s*doute\b"]),
        NegationDetectorRule(regexp=r"\bne\s*semble\s*pas"),
    ]

    #initialisation du détecteur de négations
    neg_detector = NegationDetector(output_label="is_negated", rules=neg_rules)

    #détection des négations
    neg_detector.run(syntagmas) #ne renvoie rien, ajoute un booléan à chaque syntagme pour indiquer si une négation a été détectée ou non

    #initialisation du matcher
    matcher = HFEntityMatcher(
        model="medkit/DrBERT-CASM2",
        cache_dir="models/AI/",  # <- ici on indique où chercher les fichiers
        attrs_to_copy=["is_negated"]
    )

    #detection des entités
    # On exécute le matcher sur l'ensemble des syntagmes (plus rapide)
    entities = matcher.run(syntagmas)

    results = []

    for syntagma in syntagmas:
        # Vérification de la négation du syntagme
        neg_attrs = syntagma.attrs.get(label="is_negated")
        is_negated = neg_attrs[0].value if neg_attrs else False
        
        if not is_negated:
            # On cherche si une entité "problem" a été extraite dans ce syntagme
            syntagma_entities = [e for e in entities if e.label == "problem" and e.text in syntagma.text]
            
            for entity in syntagma_entities:
                # On extrait spécifiquement le texte du problème précis (ex: "douleur thoracique")
                # au lieu de tout le contexte pour avoir un matching chirurgical.
                texte_probleme = entity.text.strip()
                if texte_probleme not in results:
                    results.append(texte_probleme)

    return(results)

if __name__ == "__main__":
    texte = "Je n'ai pas de douleurs abdominales, mais je ressens des douleurs thoraciques."
    pathologies = extract_pathologies(texte)
    print(pathologies)