# Welcom to "app"

## app tree

src : codes pour l'application \
test : codes pour les tests 

```
.app
├── README.md
├── src
│   ├── __init__.py
│   ├── app.py
│   ├── business
│   │   ├── __init__.py
│   │   ├── downloads.py
│   │   ├── matcher.py
│   │   ├── paragraphe.py
│   │   └── syntagme.py
│   ├── data
│   │   ├── csv-BDD
│   │   │   ├── chapitre.csv
│   │   │   ├── code.csv
│   │   │   └── groupe.csv
│   │   ├── aime2-cim.db
│   │   └── aime2-embeddings.npy
│   ├── models
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── orm_cim.py
│   ├── static
│   │   ├── *.css
│   │   ├── *.js
│   │   ├── *.jpeg
│   │   └── *.png
│   └── templates
│       └── *.html
└── test
    ├── business
    │   ├── test_matcher.py
    │   ├── test_paragraphe.py
    │   └── test_syntagme.py
    ├── data
    │   ├── csv-BDD
    │   │   ├── chapitre.csv
    │   │   ├── code.csv
    │   │   └── groupe.csv
    │   ├── embeddings.npy
    │   └── test.db
    ├── models
    │   ├── test_models.py
    │   └── test_orm.py
    └── README.md
```

## how to run
### requires 
- Flask
- FlaskSQLALchemy
- les modules qu'on avait déjà

### comment lancer
 - se placer dans app/src
 - executer : ```flask run``` (jsp si c'est exactement ça sous windows)