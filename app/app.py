# from flask import *
from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import * 
from orm_cim import ORM
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_cim.db'  # Remplacez par votre URI
orm = ORM("/test_cim.db")


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
    groupes = orm.session.query(Groupe.gid).all()
    fin = orm.session.query(Groupe.fin)
    description = orm.session.query(Groupe.description).all()
    values = []
    for i in range (len(groupes)) :
        values.append([groupes[i][0],fin[i][0],description[i][0]])
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
 