from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/codage')
def codage():
    return render_template('codage.html')

@app.route('/cim-x')
def cim_x():
    return render_template('cim-x.html')
