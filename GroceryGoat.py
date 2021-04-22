from flask import Flask, render_template, request, session, redirect, url_for, g, flash
import os
import json
import pandas as pd
import requests

IMAGE_FOLDER = os.path.join('static', 'images')

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
    return render_template('GGHome.html', home_shopping_image = Floating_shopping, home_recipe_image = recipe_template)
    if not g.user:
        return redirect(url_for('login'))

@app.route('/Lists')
def lists():
    print("Lists pressed")
    return render_template('GGLists.html')

@app.route('/Recipes', methods = ["GET", "POST"])
def recipes():
    if request.method == "POST":
        recipe_input = request.form.get("search")
        recipe_amount = request.form.get("amount")
        print(recipe_input)
        print(recipe_amount)
        allRecipes = requests.get('https://api.edamam.com/search?q=' + recipe_input + '&app_id=c4fad94b&app_key=67c768fc1f825a76bea9f5ca1975eb4e&from=0')
        allRecipesDic = json.loads(allRecipes.text)
        recipeDic = allRecipesDic["hits"]
        count = 0
        for i in allRecipesDic["hits"]:
        	recipeDic[count] = i["recipe"]
        	count += 1
        with open('data.json', 'w') as outfile:
            json.dump(recipeDic, outfile)
        df = pd.DataFrame(recipeDic)
        df = df.drop(labels=["digest", "totalDaily", "totalNutrients", "ingredients", "shareAs", "totalWeight", "uri"], axis=1)
        return df.to_html()
    return render_template('GGRecipe.html')

@app.route('/Login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		session.pop('user_id', None)

		username = request.form['username']
		password = request.form['password'] 

		user = [x for x in users if x.email == username]
		if len(user) > 0:
			user = user[0]
		else:
			flash("Login info is incorrect", "info")
			return redirect(url_for('login'))
		if user and user.password == password:
			session['user_id'] = user.id
			return redirect(url_for('main'))
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

@app.route('/Signup')
def signup():
    print("test")
    return render_template('GGSignup.html')

@app.route('/Contact')
def contact():
    return render_template('contact.html')

@app.route('/Account')
def account():
    return render_template('GGAccount.html')

if __name__ == '__main__':
    app.run()
