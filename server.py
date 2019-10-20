import os
import json
from collections import OrderedDict
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


def match1Nutri(ch,value,perfer=None):
  col=int()
  res = list()
  limits = int()
  res = db_query("SELECT * FROM nutrition WHERE NAME like " + "\"%"+ perfer +"%\"" if perfer is not None else "SELECT * FROM nutrition" )
  if ch =='c' or ch == 'C':
    col=5
    limits = crange
  elif ch == 'p' or ch == 'P':
    col=3
    limits = prange
  elif ch == 'f' or ch == 'F':
    col=4
    limits = frange
  else:
    raise Exception('Precondition not satisfied')

  for i in range(len(res)-1,-1,-1):
      if abs(float(res[i][col])-value) > limits:
        res.pop(i)

  return set(res)

def removeAllergies(potentData,allergies):
  for i in range(len(potentData)-1,-1,-1):
    for allergy in allergies:
      if potentData[i][2].find(allergy) != -1 :
        potentData.pop(i)

def match(carb,prot,fat,first=3,perferedcat=[],allergies=[]):
  if perferedcat == []:
    carbnear = match1Nutri('c',carb)
    protnear = match1Nutri('p',prot)
    fatnear = match1Nutri('f',fat)
    potentData = carbnear.union(protnear,fatnear)
  else:
    potentData = set()
    for x in perferedcat:
      carbnear = match1Nutri('c',carb,x)
      protnear = match1Nutri('p',prot,x)
      fatnear = match1Nutri('f',fat,x)
      potentData =potentData.union(carbnear,protnear,fatnear)

  potentData = list(potentData)
  for i in range(len(potentData)):
    error = (abs(float(potentData[i][3])-prot) + abs(float(potentData[i][4])-fat) + abs(float(potentData[i][5])-carb)) ,
    mrec = potentData[i] + error
    potentData[i]= mrec
  potentData = sorted(potentData,key = lambda x: float(x[len(x)-1]))
  if allergies != []:
    removeAllergies(potentData,allergies)
  return potentData[:first]

def userPrefer(username):
  res = db_query("SELECT * FROM USERPREFERENCE WHERE username = \""+username+"\"")
  tagCount=OrderedDict()
  for rec in res:
    tags = rec[1].split(',')
    for tag in tags:
      if tag not in tagCount.keys():
        tagCount[tag] = 1
      else:
        tagCount[tag] += 1
  tagCount = OrderedDict(sorted(tagCount.items(),key = lambda x: x[1] ))
  return list(tagCount.keys())




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
    carbs = int(round(float(request.form['carbs'])))
    protein = int(round(float(request.form['protein'])))
    fat = int(round(float(request.form['fat'])))
    allergies = request.form['allergies'].split(';') if request.form['allergies'] !='' else []
    res = set(match(carbs,protein,fat,first=2,allergies=allergies))
    for x in match(carbs,protein,fat,first=3,allergies=allergies,perferedcat=[]):
      res.add(x)
      if len(res) == 3:
        break
    res = list(res)
    return json.dumps(res)

app.run(host='0.0.0.0', port=5000)
