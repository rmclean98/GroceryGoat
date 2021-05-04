from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from flask_sqlalchemy import SQLAlchemy
import os
import json
import pandas as pd
import requests
from app import app


IMAGE_FOLDER = os.path.join('static', 'images')
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'tempsecretkey'
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(basedir, 'GG.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from model.Model import db
from model.Model import ListDetails
from model.Model import GroceryLists
from model.Model import Users
from model.Model import Todo
db.create_all()

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        #user = [x for x in users if x.id == session['user_id']]
        g.user = session['user_id']
        print(g.user)

@app.route('/')
@app.route('/index')
def main():
    if not g.user:
        return redirect(url_for('login'))
    Floating_shopping = os.path.join(app.config['IMAGE_FOLDER'], 'Floating_shopping_list.png')
    recipe_template = os.path.join(app.config['IMAGE_FOLDER'], 'recipe_template.png')

    x = session['user_id']
    currentuser = Users.query.with_entities(Users.fname).filter(Users.userId==x).all()
    for y in currentuser:
    	currentuser = y.fname
    return render_template('GGHome.html', home_shopping_image = Floating_shopping, home_recipe_image = recipe_template,userFName=currentuser )


@app.route('/add', methods=['POST'])
def add():
	todo = Todo(text=request.form['todoitem'], complete=False)
	db.session.add(todo)
	db.session.commit()
	return redirect(url_for('lists'))


@app.route('/Lists')
def lists():
	if 'user_id' in session:
		x = session['user_id']
		users_lists = ListDetails.query.with_entities(ListDetails.userId).filter(ListDetails.userId==x).all()
		if len(users_lists)==0:
			print('user has no lists')
			return render_template('GGLists.html', incomplete=incomplete, complete=complete)
		incomplete = Todo.query.filter_by(complete=False).all()
		complete = Todo.query.filter_by(complete=True).all()
		return render_template('GGLists.html', incomplete=incomplete, complete=complete)
	return redirect(url_for('login'))

@app.route('/complete/<id>')
def complete(id):
  
#   using the todo object from the session thats filter by this id. this way we're changing the value of 
#   todo itme in the db session
    todo = db.session.query(Todo).filter_by(id=int(id)).first()
    todo.complete = True
    db.session.commit()
  
    return redirect(url_for('lists'))

@app.route('/Recipes', methods = ["GET", "POST"])
def recipes():
    if request.method == "POST":
        recipe_input = request.form.get("search")
        recipe_amount = request.form.get("amount")
        if(recipe_input == ""):
            alertOption="alert alert-success"
            confirmMessage0='Search Failed'
            confirmMessage1='Enter a value into the search box'
            confirmMessage2=''
            redirection='/Recipes'
            return render_template('confirmation.html',alertOption=alertOption,confirmMessage0=confirmMessage0,confirmMessage1=confirmMessage1,confirmMessage2=confirmMessage2,redirection=redirection)
        allRecipes = requests.get('https://api.edamam.com/search?q=' + recipe_input + '&app_id=c4fad94b&app_key=67c768fc1f825a76bea9f5ca1975eb4e&from=0&to=' + recipe_amount)
        allRecipesDic = json.loads(allRecipes.text)
        recipes = cleanData(allRecipesDic)
        ingredients = recipes[0][8].split(', ')
        healthlabel = recipes[0][6].split(', ')
        print(ingredients)
        return render_template('GGRecipe.html',recipeLists=recipes, ingredients=ingredients,healthlabel=healthlabel)
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
			alertOption="alert alert-success"
			confirmMessage0='Congratulations'
			confirmMessage1='Login successfully!'
			confirmMessage2=''
			redirection='/Lists'
			return render_template('confirmation.html',alertOption=alertOption,confirmMessage0=confirmMessage0,confirmMessage1=confirmMessage1,confirmMessage2=confirmMessage2,redirection=redirection)
		else:
			alertOption="alert alert-danger"
			confirmMessage0='Whoops'
			confirmMessage1='Your login has failed!'
			confirmMessage2='incorrect username/password.'
			redirection='/Login'
			return render_template('confirmation.html',alertOption=alertOption,confirmMessage0=confirmMessage0,confirmMessage1=confirmMessage1,confirmMessage2=confirmMessage2,redirection=redirection)
		return redirect(url_for('login'))
	return render_template('GGLogin.html')

@app.route('/Logout')
def logout():
	if 'user_id' in session:
		session.pop('user_id', None)
		alertOption="alert alert-success"
		confirmMessage0='Bye have a great time'
		confirmMessage1='You have logged out successfully!'
		confirmMessage2='Come see us again.'
		redirection='/Login'
		return render_template('confirmation.html',alertOption=alertOption,confirmMessage0=confirmMessage0,confirmMessage1=confirmMessage1,confirmMessage2=confirmMessage2,redirection=redirection)


@app.route('/Signup', methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		check = Users.query.with_entities(Users.userId).filter(Users.emailId==request.form.get('email')).all()
		if(len(check) > 0):
			alertOption="alert alert-danger"
			confirmMessage0='Whoops'
			confirmMessage1='Your account creation has failed!'
			confirmMessage2='username is already in use.'
			redirection='/Signup'
			return render_template('confirmation.html',alertOption=alertOption,confirmMessage0=confirmMessage0,confirmMessage1=confirmMessage1,confirmMessage2=confirmMessage2,redirection=redirection)
		else:
			user = Users(emailId=request.form.get('email'),password=request.form.get('password'),fname=request.form.get('firstname'),lname=request.form.get('lastname'))
			print(user)
			db.session.add(user)
			db.session.commit()
			alertOption="alert alert-success"
			confirmMessage0='Sheesh nice job'
			confirmMessage1='Your registration has been completed successfully!'
			confirmMessage2='Please login with your user credentials.'
			redirection='/Lists'
			#session['user_id'] = Users.query.with_entities(Users.userId,Users.emailId).filter(Users.emailId==username).filter(Users.password==password).all()
			return render_template('confirmation.html',alertOption=alertOption,confirmMessage0=confirmMessage0,confirmMessage1=confirmMessage1,confirmMessage2=confirmMessage2,redirection=redirection)

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
