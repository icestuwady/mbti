from flask import Flask, render_template, request, redirect, url_for, session 
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import re
import altair as alt
import pandas as pd 
import numpy as np 
import joblib 
import json
import plotly
import plotly.express as px

app = Flask(__name__)

pipe_lr = joblib.load(open("model/final_model_teatea.pkl","rb"))

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'sr_project'

# Intialize MySQL
mysql = MySQL(app)

#home
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/personality')
def personality():
    return render_template('Personality.html')

@app.route('/personalitylogin')
def personalitylogin():
    return render_template('Personality_login.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
     # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['name'] = account['name']
            # Redirect to home page
            return render_template('Prediction.html')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password! Try Again'
    # Show the login form with message (if any)
    return render_template('signin.html', msg=msg)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Output message if something goes wrong...
    msg = ''
    msgE =''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msgE = 'Error: username is already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msgE = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msgE = 'Username must contain only characters and numbers!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msgE = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not name:
            msgE = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s)', (username, name, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('signup.html', msg=msg, msgE=msgE)

@app.route('/signuppage')
def signuppage():
    return render_template('signup.html')

@app.route('/predict')
def predict():
    return render_template('Prediction.html')

@app.route('/prediction', methods = ["POST"])
def prediction():
    yourmbti = request.form['select']
    yourpost = request.form['text_post']
    prediction = pipe_lr.predict([yourpost])
    probability = pipe_lr.predict_proba([yourpost])

    proba_df = pd.DataFrame(probability*100, columns=pipe_lr.classes_)

    username = session['username']
    date = datetime.now()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO history VALUES (%s, %s, %s, %s, %s, %s)', (username, date, yourpost, yourmbti, prediction[0], "{:.4f}".format(np.max(probability[0]*100)),))
    mysql.connection.commit()
    fig = px.bar(proba_df.T)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('show.html', probability="Confidence: {:.4f} %".format(np.max(probability[0]*100)), 
                                        prediction= prediction[0], 
                                        yourtype=yourmbti, 
                                        proba_df=proba_df,
                                        tables = [proba_df.to_html(classes = 'data')],
                                        graphJSON=graphJSON)

@app.route('/signout')
def signout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('name', None)
    # Redirect to login page
    return render_template('index.html')

@app.route('/enfj')
def enfj():
    return render_template('enfj.html')

@app.route('/enfp')
def enfp():
    return render_template('enfp.html')

@app.route('/entj')
def entj():
    return render_template('entj.html')

@app.route('/entp')
def entp():
    return render_template('entp.html')

@app.route('/esfj')
def esfj():
    return render_template('esfj.html')

@app.route('/esfp')
def esfp():
    return render_template('esfp.html')

@app.route('/estj')
def estj():
    return render_template('estj.html')

@app.route('/estp')
def estp():
    return render_template('estp.html')

@app.route('/infj')
def infj():
    return render_template('infj.html')

@app.route('/infp')
def infp():
    return render_template('infp.html')

@app.route('/intj')
def intj():
    return render_template('intj.html')

@app.route('/intp')
def intp():
    return render_template('intp.html')

@app.route('/isfj')
def isfj():
    return render_template('isfj.html')

@app.route('/isfp')
def isfp():
    return render_template('isfp.html')

@app.route('/istj')
def istj():
    return render_template('istj.html')

@app.route('/istp')
def istp():
    return render_template('istp.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/about_l')
def about_l():
    return render_template('about_l.html')

@app.route('/history')
def history():
    username = session['username']

    cur = mysql.connection.cursor()
    cur.execute('SELECT dateday,posts,test,model,Confidence FROM history WHERE username = %s ORDER BY dateday DESC',(username,))
    data = cur

    return render_template('history.html', history=data ,username=username)

if __name__ == "__main__":
    app.run(debug=True)