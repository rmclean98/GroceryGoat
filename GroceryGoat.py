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

@app.route('/addList', methods=['POST'])
def addList():
	x = session['user_id']
	ln = request.form.get('listname')
	list = ListDetails(listTitle=ln,userId=x)
	db.session.add(list)
	db.session.commit()
	return redirect(url_for('lists'))

@app.route('/showList/<listId>')
def showList(listId):
	title = None
	x = session['user_id']
	users_lists = ListDetails.query.with_entities(ListDetails.userId, ListDetails.listTitle,ListDetails.listId).filter(ListDetails.userId==x).all()
	for i in users_lists:
		if (int(i.listId) == int(listId)):
			title = i.listTitle
	#incomplete = Todo.query.with_entities(Todo).filter(Todo.complete==False).filter(Todo.listId==listId).all()
	#complete = Todo.query.with_entities(Todo).filter(Todo.complete==True).filter(Todo.listId==listId).all()
	status = Todo.query.with_entities(Todo.text, Todo.complete, Todo.id).filter(Todo.listId==listId).all()
	return render_template('GGLists.html', status = status,lists = users_lists, listId=title, currentID=int(listId))

	

@app.route('/addItem/<listId>', methods=['POST'])
def addItem(listId):
	if(int(listId) == 0):
		print("not in here ")
		return redirect(url_for('lists'))
	else:
		print("here")
		input = request.form['todoitem']
		if(input is None):
			#redirect confirmation popup
			return redirect(url_for('lists'))
		todo = Todo(listId=listId, text=request.form['todoitem'], complete=False)
		db.session.add(todo)
		db.session.commit()
		return redirect(url_for('showList', listId=listId))
	



@app.route('/Lists')
def lists():
	if 'user_id' in session:
		x = session['user_id']
		users_lists = ListDetails.query.with_entities(ListDetails.userId, ListDetails.listTitle,ListDetails.listId).filter(ListDetails.userId==x).all()
		if len(users_lists)==0:
			print('user has no lists')
			#incomplete = Todo.query.with_entities(Todo).filter(Todo.complete==False).filter(Todo.listId==users_lists[0].listId).all()
			#complete = Todo.query.with_entities(Todo).filter(Todo.complete==True).filter(Todo.listId==users_lists[0].listId).all()
			status = Todo.query.with_entities(Todo.text, Todo.complete, Todo.id).filter(Todo.listId==0).all()
			return render_template('GGLists.html', status=status, lists = users_lists, listId=0, currentID=0)
		#incomplete = Todo.query.with_entities(Todo,).filter(Todo.complete==False).filter(Todo.listId==users_lists[0].listId).all()
		status = Todo.query.with_entities(Todo.text, Todo.complete, Todo.id).filter(Todo.listId==users_lists[0].listId).all()
		#print(status)
		return render_template('GGLists.html', status=status, lists = users_lists, listId=users_lists[0].listTitle, currentID=users_lists[0].listId)
	return redirect(url_for('login'))

@app.route('/complete/<id>')
def complete(id):
	todo = Todo.query.filter(Todo.id==id).first()	
	listNum = todo.listId

	if(todo.complete == False):
		todo.complete = True
	else:
		todo.complete = False
	db.session.commit()
  
	return redirect(url_for('showList', listId=listNum))

@app.route('/addToList/<ing>/<id>')
def addToList(ing, id):
	with open('data.json') as json_file:
		data = json.load(json_file)
		#print(data)
	todo = Todo.query.filter(Todo.id==id).first()
	tmp = None
	for p in data[int(ing)]['ingredients']:
		if(tmp is not p['text']):
			tmp = p['text']
			newing = Todo(listId=id, text=p['text'], complete=False)
			db.session.add(newing)
		
	db.session.commit()
	
	return redirect(url_for('showList', listId=id))

@app.route('/delList/<listId>')
def delList(listId):
	ld = ListDetails.query.filter_by(listId=int(listId)).first()
	todo = Todo.query.filter(Todo.listId==listId).all()
	
	
	for bye in todo:
		db.session.delete(bye)

	db.session.delete(ld)
	db.session.commit()
  
	return redirect(url_for('lists'))

@app.route('/Recipes', methods = ["GET", "POST"])
def recipes():
	if request.method == "POST":
		x = session['user_id']
		users_lists = ListDetails.query.with_entities(ListDetails.userId, ListDetails.listTitle,ListDetails.listId).filter(ListDetails.userId==x).all()
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
		with open('data.json', 'w') as outfile:
			json.dump(allRecipesDic, outfile)
		recipes = cleanData(allRecipesDic)
		for i in recipes:
			i[8] = i[8].split(', ')
			i[6] = i[6].split(', ')
		return render_template('GGRecipe.html',recipeLists=recipes, userslist=users_lists)
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
			uEmail = request.form.get('email')
			user = Users(emailId=uEmail,password=request.form.get('password'),fname=request.form.get('firstname'),lname=request.form.get('lastname'))
			print(user)
			db.session.add(user)
			db.session.commit()
			alertOption="alert alert-success"
			confirmMessage0='Sheesh nice job'
			confirmMessage1='Your registration has been completed successfully!'
			confirmMessage2='Please login with your user credentials.'
			redirection='/Lists'
			newUser = Users.query.with_entities(Users.userId).filter(Users.emailId==uEmail).all()
			for i in newUser:
				k = i.userId
			session['user_id'] = k
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
    app.run(debug = True)
