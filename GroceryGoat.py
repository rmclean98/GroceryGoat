from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from flask_sqlalchemy import SQLAlchemy
import os
import json
import pandas as pd
import requests

IMAGE_FOLDER = os.path.join('static', 'images')
basedir = os.path.abspath(os.path.dirname(__file__))

class User:
	def __init__(self, id, firstname, lastname, email, password):
		self.id = id
		self.firstname = firstname
		self.lastname = lastname
		self.email = email
		self.password =  password
	def __repr__(self):
		return f'<User: {self.firstname} {self.lastname}>'

users = []
users.append(User(id=1, firstname = 'Brandon', lastname = 'Fellenstein', email = 'fellensteinb17@students.ecu.edu', password = 'TestPass'))
users.append(User(id=2, firstname = 'Jon', lastname = 'Doe', email = 'jondoe@gmail.com', password = 'password'))

print(users)

app = Flask(__name__)
app.secret_key = 'tempsecretkey'
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(basedir, 'GG.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from model.Model import db
from model.Model import ListDetails
from model.Model import GroceryLists
from model.Model import Users
db.create_all()

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route('/')
def main():
    Floating_shopping = os.path.join(app.config['IMAGE_FOLDER'], 'Floating_shopping_list.png')
    recipe_template = os.path.join(app.config['IMAGE_FOLDER'], 'recipe_template.png')
    if not g.user:
        return redirect(url_for('login'))

    x = session['user_id']
    currentuser = Users.query.with_entities(Users.fname).filter(Users.userId==x).all()
    for y in currentuser:
    	currentuser = y.fname
    return render_template('GGHome.html', home_shopping_image = Floating_shopping, home_recipe_image = recipe_template,userFName=currentuser )

@app.route('/Lists')
def lists():
    print("Lists pressed")
    return render_template('GGLists.html')

@app.route('/Recipes', methods = ["GET", "POST"])
def recipes():
    if request.method == "POST":
        recipe_input = request.form.get("search")
        recipe_amount = request.form.get("amount")
        allRecipes = requests.get('https://api.edamam.com/search?q=' + recipe_input + '&app_id=c4fad94b&app_key=67c768fc1f825a76bea9f5ca1975eb4e&from=0&to=' + recipe_amount)
        allRecipesDic = json.loads(allRecipes.text)
        recipes = cleanData(allRecipesDic)
        return render_template('GGRecipe.html',recipeLists=recipes)
    return render_template('GGRecipe.html')

@app.route('/Login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		session.pop('user_id', None)

		username = request.form['username']
		password = request.form['password'] 
		records = Users.query.with_entities(Users.userId,Users.emailId).filter(Users.emailId==username).filter(Users.password==password).all()
		list1=[]
		for x in records:
			list2={}
			list2['userId'] = x.userId
			list2['emailId'] = x.emailId
			list1.append(list2)
			
		if len(list1) > 0:
			list1 = list1[0]
			session['user_id'] = list1['userId']
			return redirect(url_for('main'))
		else:
			flash("Login info is incorrect", "info")
			return redirect(url_for('login'))
		return redirect(url_for('login'))
	return render_template('GGLogin.html')

@app.route('/Logout')
def logout():
	if 'user_id' in session:
		session.pop('user_id', None)
		flash("User logged out succesfully", "info")
		return redirect(url_for('login'))
	print("no user to log out")
	return redirect(url_for('account'))

@app.route('/Signup', methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		user = Users(emailId=request.form.get('email'),password=request.form.get('password'),fname=request.form.get('firstname'),lname=request.form.get('lastname'))
		print(user)
		db.session.add(user)
		db.session.commit()
		confirmMessage1='Your registration has been completed successfully!'
		confirmMessage2='Please login with your user credentials.'
		redirection='/'
		return render_template('confirmation.html',confirmMessage1=confirmMessage1,confirmMessage2=confirmMessage2,redirection=redirection)

	return render_template('GGSignup.html')
@app.route('/Contact')
def contact():
    return render_template('contact.html')

@app.route('/Account')
def account():
    return render_template('GGAccount.html')
    
def cleanData(recipes):
	recipeDic = recipes["hits"]
	count = 0
	for i in recipes["hits"]:
		recipeDic[count] = i["recipe"]
		count += 1
	with open('data.json', 'w') as outfile:
		json.dump(recipeDic, outfile)
	df = pd.DataFrame(recipeDic)
	df = df.drop(labels=["digest", "totalDaily", "totalNutrients", "ingredients", "shareAs", "totalWeight", "uri"], axis=1)
        
	special_char = ["[", """'""", "]"]
	df = df.astype(str)
	for col in df.columns:
		for char in special_char:
			df[col] = df[col].str.replace(char,'', regex=True)
	return df.values.tolist()

if __name__ == '__main__':
    app.run()
