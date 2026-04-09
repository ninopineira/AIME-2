# from flask import *
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from .models.orm_cim import ORM
from .business.matcher import Matcher
from .models.models import Groupe, Code, Chapitre
from pathlib import Path
from .business.syntagme import extract_pathologies
from .business.paragraphe import extract_text
import os
import threading
from dotenv import load_dotenv

# Charge les variables du fichier .env (à la racine du projet)
load_dotenv()

app = Flask(__name__)

# Clé secrète pour les sessions — définir AIME_SECRET_KEY en variable d'environnement en production
app.secret_key = os.environ.get('AIME_SECRET_KEY', 'aime-dev-secret-2024-changez-en-prod')

# Code admin — définir AIME_ADMIN_CODE en variable d'environnement pour personnaliser
ADMIN_CODE = os.environ.get('AIME_ADMIN_CODE', 'AIME-ADMIN-2024')
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
    data = {'data' : values, 'title':"Liste des codes Cim-X", 'colonnes': ["Code","Description"]}
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
 
@app.route('/codage',methods=["GET","POST"])
def codage():
    print(request.form)
    if not request.form :
        return render_template('codage.html')
    else :
        donnees = request.form
        texte_courrier = donnees.get('texte-courrier')
        texte = donnees.get('texte')
        # print(type(texte))
        # print("========================HERE=============",texte_courrier)
        if texte_courrier: #"courrier"
            synt = []
            for elt in extract_text(texte) :
                synt = synt + (extract_pathologies(elt))
        else :
            print(extract_text(texte))
            synt = extract_pathologies(texte)
            print("cas a la con ",texte_courrier)

        results = matcher.match_cim10(synt)
        # print(synt)
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


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        code = request.form.get('adminCode', '')
        if code == ADMIN_CODE:
            session['admin_logged'] = True
            return redirect(url_for('adminCimX'))
        else:
            return render_template('admin-login.html', error="Code incorrect. Accès refusé.")
    return render_template('admin-login.html')

@app.route('/admin/logout')
def adminLogout():
    session.pop('admin_logged', None)
    return redirect(url_for('admin'))

@app.route('/admin/cim-x')
def adminCimX():
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))
    return render_template('cim-x.html')

# Statut du recalcul des embeddings (partagé entre threads)
_embed_status = {'running': False, 'done': False, 'error': None}

@app.route('/admin/cim-x/rechargement', methods=['GET', 'POST'])
def adminCimXRechargement():
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))

    if request.method == 'GET':
        return render_template('cim-x-rechargement.html')

    fichier = request.files.get('csv_codes')
    if not fichier or not fichier.filename.lower().endswith('.csv'):
        return render_template('cim-x.html', error="Fichier CSV invalide ou manquant.")

    upload_path = current_dir / "data" / "csv-BDD" / "code.csv"
    try:
        fichier.save(str(upload_path))
        orm.reload_codes(upload_path)
    except Exception as e:
        return render_template('cim-x-rechargement.html', error=f"Erreur lors du rechargement : {e}")

    # Recalcul des embeddings en arrière-plan
    def _recompute():
        _embed_status['running'] = True
        _embed_status['done'] = False
        _embed_status['error'] = None
        try:
            orm.recompute_cim10('FremyCompany/BioLORD-2023-M')
            matcher.reload_cim10()  # recharge codes + descriptions + embeddings en mémoire
            _embed_status['done'] = True
        except Exception as exc:
            _embed_status['error'] = str(exc)
        finally:
            _embed_status['running'] = False

    t = threading.Thread(target=_recompute, daemon=True)
    t.start()

    return render_template('cim-x-rechargement.html',
                           success="Codes CIM-X rechargés avec succès. Recalcul des embeddings en cours…")

@app.route('/admin/cim-x/rechargement/status')
def adminCimXRechargementStatus():
    if not session.get('admin_logged'):
        return jsonify({'error': 'non autorisé'}), 403
    return jsonify(_embed_status)

@app.route('/admin/cim-x/affichage')
def adminCimXAffichage():
    if not session.get('admin_logged'):
        return redirect(url_for('admin'))
    codes_list = orm.session.query(Code.cid).all()
    descriptions = orm.session.query(Code.description).all()
    values = []
    for i in range(len(codes_list)):
        values.append([codes_list[i][0], descriptions[i][0]])
    data = {'data': values, 'title': 'Liste des codes CIM-10', 'colonnes': ['Code', 'Description']}
    return render_template('table.html', data=data)