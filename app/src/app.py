# from flask import *
from flask import Flask, request , render_template
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import * 
from .models.orm_cim import ORM
from .models.models import Groupe, Code, Chapitre
from pathlib import Path
from .business.syntagme import extract_pathologies
from .business.matcher import Matcher
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test_cim.db'  # Remplacez par votre URI

#chemin vers le script 
current_dir = Path(__file__).resolve().parent
pathDB = current_dir / "data" / "aime2-cim.db"
pathEMB = current_dir / "data" / "aime2-embeddings.npy"
orm = ORM(pathDB,pathEMB) #modif pour json
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
def groupes():
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
def chapitres():
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

    synt = extract_pathologies(texte)
    results = matcher.match_cim10(synt)
    print(synt)
    print(results)
    values = []
    for entry in results :
        ref = entry.get('entity')
        c1 = entry.get('best_match_code')
        d1 = entry.get('best_match_description')
        c2 = entry.get('second_best_match_code')
        d2 = entry.get('second_best_match_description')
        c3 = entry.get('third_best_match_code')
        d3 = entry.get('third_best_match_description')
        
        # Si notre IA n'a rien trouvé avec un score au-dessus du seuil (None),
        # on ignore complètent ce résultat pour ne pas polluer l'affichage de l'utilisateur.
        if not c1:
            continue
            
        def get_group_chapter(code_str):
            code_obj = orm.session.query(Code).filter(Code.cid == code_str).first()
            if code_obj and code_obj.groupes and code_obj.groupes.chapitres:
                return code_obj.groupes.gid, code_obj.groupes.description, code_obj.groupes.chapitres.chid, code_obj.groupes.chapitres.description
            return "", "", "", ""

        def add_value(ref, code_str, desc_str):
            gid, gdesc, chid, chdesc = get_group_chapter(code_str)
            values.append({
                "ref": ref,
                "code": code_str,
                "description": desc_str,
                "gid": gid,
                "gdesc": gdesc,
                "chid": chid,
                "chdesc": chdesc
            })

        add_value(ref, c1, d1)
            
        if c2:
            add_value(ref, c2, d2)
        if c3:
            add_value(ref, c3, d3)

    data = {
        'texte': texte,
        'data' : values, 
        'title': "Resultats de recherche", 
        'colonnes': ["Référence à", "Code", "Description", "Groupe", "Chapitre"]
    }
    return render_template('codageResults.html', data=data)

@app.route('/admin')#methods post
def admin():
    #charger le fichier avec mdp
    #decrypter le mdp
    #comparer avec le request.form
    return 