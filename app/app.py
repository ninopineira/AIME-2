from flask import *
from sqlalchemy import * 
from orm_cim import ORM
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_cim.db'  # Remplacez par votre URI
orm = ORM("/test_cim.db")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/codage')
def codage():
    return render_template('codage.html')

@app.route('/cimx')
def cimx():
    code = orm.session.query(Code).all()
    return render_template('cim-x.html',code=code)

@app.route('/chapitres') #aura pour vocation à disparaitre
def chapitre():
    chapitre = orm.session.query(Chapitre).all()
    # print(chapitre)
    return render_template('chapitre.html',chapitre=chapitre)

@app.route('/groupes')
def groupe():
    recherche = request.args.get('recherche', '')

    # Si une recherche est effectuée
    if recherche:
        groupe = orm.session.query(Groupe).filter(
            or_(
                Groupe.description.ilike(f'%{recherche}%'),
                Groupe.gid.ilike(f'%{recherche}%')
            )
        ).all()
    else:
        groupe = orm.session.query(Groupe).all()

    return render_template('groupe.html', groupe=groupe, recherche=recherche)


 