import os
import json
from flask import Flask
from flask import render_template
from flask import request
import mysql.connector

app = Flask(__name__)

prange = 10
frange = 10
crange = 10

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
    return cursor.fetchall()


def match1Nutri(ch,value):
  col=int()
  res = list()
  limits = int()
  if ch =='c' or ch == 'C':
    col=5
    res = db_query("SELECT * FROM nutrition")
    limits = crange
  elif ch == 'p' or ch == 'P':
    col=3
    res = db_query("SELECT * FROM nutrition")
    limits = prange
  elif ch == 'f' or ch == 'F':
    col=4
    res = db_query("SELECT * FROM nutrition")
    limits = frange
  else:
    raise Exception('Precondition not satisfied')

  for i in range(len(res)-1,-1,-1):
      if abs(float(res[i][col])-value) > limits:
        res.pop(i)

  return set(res)


def match(carb,prot,fat,first=3):
  print( db_query("SELECT * FROM nutrition"))
  carbnear = match1Nutri('c',carb)
  protnear = match1Nutri('p',prot)
  fatnear = match1Nutri('f',fat)
  potentData = carbnear.union(protnear,fatnear)
  potentData = list(potentData)
  for i in range(len(potentData)):
    error = (abs(float(potentData[i][3])-prot) + abs(float(potentData[i][4])-fat) + abs(float(potentData[i][5])-carb)) ,
    mrec = potentData[i] + error
    potentData[i]= mrec
  return sorted(potentData,key = lambda x: x[len(x)-1])[:first]

print(match(12,10,10))

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

@app.route("/getMeals", methods=['POST'])
def getMeals():
    carbs = int(request.form['carbs'])
    protein = int(request.form['protein'])
    fat = int(request.form['fat'])
    return json.dumps(match(carbs,protein,fat,first=3))

app.run(host='0.0.0.0', port=5000)
