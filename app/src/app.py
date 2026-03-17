# from flask import *
from flask import Flask, request , render_template
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import * 
from .models.orm_cim import ORM
from .business.matcher import Matcher
from .models.models import Groupe, Code, Chapitre
from pathlib import Path
from .business.syntagme import extract_pathologies
from .business.paragraphe import extract_text
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test_cim.db'  # Remplacez par votre URI

#chemin vers le script 
current_dir = Path(__file__).resolve().parent
pathDB = current_dir / "data" / "aime2-cim.db"
pathEMB = current_dir / "data" / "aime2-embeddings.npy"
orm = ORM(pathDB,pathEMB)
matcher = Matcher('FremyCompany/BioLORD-2023-M',orm)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/codes')
def codes():
    codes = orm.session.query(Code.cid).all()
    description = orm.session.query(Code.description).all()
    values = []
    for i in range (len(codes)) :
        values.append([codes[i][0],description[i][0]])
    data = {'data' : values, 'title':"Liste des codes Cim-X", 'colonnes': ["Code","Déscription"]}
    return render_template('table.html',data=data)

@app.route('/groupes')
def groupe():
    gid = orm.session.query(Groupe.gid).all()
    fin = orm.session.query(Groupe.fin).all()
    description = orm.session.query(Groupe.description).all()
    values = []
    for i in range (len(gid)) :
        values.append([gid[i][0],fin[i][0],description[i][0]]) #\ufeffA00
    print(gid)
    data = {'data' : values, 'title':"Groupes de la Cim-X", 'colonnes': ["Début","Fin","Déscription"]}
    return render_template('table.html',data=data)

@app.route('/chapitres')
def chapitre():
    chapitres = orm.session.query(Chapitre.chid).all()
    description = orm.session.query(Chapitre.description).all()
    values = []
    for i in range (len(chapitres)) :
        values.append([chapitres[i][0],description[i][0]])
    data = {'data' : values, 'title':"Chapitres de la Cim-X", 'colonnes': ["Numéro de Chapitre","Titre"]}
    return render_template('table.html',data=data)
 
@app.route('/codage')
def codage():
    return render_template('codage.html')

@app.route('/codage/traitement',methods=["POST"])
def traitement() :
    donnees = request.form
    texte_courrier = donnees.get('texte-courrier')
    texte = donnees.get('texte')
    print(type(texte))
    print("========================HERE=============",texte_courrier)
    if texte_courrier: #"courrier"
        synt = []
        for elt in extract_text(texte) :
            synt = synt + (extract_pathologies(elt))
    else :
        print(extract_text(texte))
        synt = extract_pathologies(texte)
        print("cas a la con ",texte_courrier)

    results = matcher.match_cim10(synt)
    print(synt)
    # print(results)
    values = []
    for entry in results :
        ref = entry.get('entity')
        c1 = entry.get('best_match_code')
        d1 = entry.get('best_match_description')
        c2 = entry.get('second_best_match_code')
        d2 = entry.get('second_best_match_description')
        c3 = entry.get('third_best_match_code')
        d3 = entry.get('third_best_match_description')
        values.append([ref,c1,d1])
        values.append([ref,c2,d2])
        values.append([ref,c3,d3])
    data = {'texte':texte,'data' : values, 'title':"Resultats de recherche", 'colonnes': ["Référence à","Code","description"]}
    return render_template('codageResults.html',data=data)