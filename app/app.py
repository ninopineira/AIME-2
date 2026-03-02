# from flask import *
from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import * 
from business.orm_cim import ORM
from business.models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test_cim.db'  # Remplacez par votre URI
orm = ORM("data/test_cim.db")


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/codage')
def codage():
    return render_template('codage.html')

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
 