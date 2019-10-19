import os
from flask import Flask
from flask import render_template
import mysql.connector

app = Flask(__name__)

def db_query(q):   
    c = mysql.connector.connect(
      host="localhost",
      database="hackathon",
      user="root",
      passwd=""
    )

    cursor = c.cursor(buffered=True)

    query = (q)
    cursor.execute(query)

    for (r) in cursor:
        if (float(r[1])>20):
            print(r)
        
db_query("SELECT name, protein FROM nutrition WHERE protein >= 5")
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signUp")
def signUp():
    return render_template('signUp.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

app.run(host='0.0.0.0', port=5000)
