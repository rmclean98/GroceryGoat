from flask import Flask, render_template, request, session, redirect, url_for, g
import os
import requests
import json

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
def coupons():
    print("Lists pressed")
    return render_template('GGLists.html')

@app.route('/Recipes', methods = ["GET", "POST"])
def recipes():
    if request.method == "POST":
        recipe_input = request.form.get("search")
        print(recipe_input)
        allRecipes = requests.get('https://api.edamam.com/search?q=chicken&app_id=c4fad94b&app_key=67c768fc1f825a76bea9f5ca1975eb4e&from=0&to=3')
        allRecipesDic = json.loads(allRecipes.text)
        x = json.dumps(allRecipesDic, sort_keys=True, indent=4)
        print(x)
        with open('data.txt', 'w') as outfile:
            json.dump(x, outfile)
        return recipe_input + allRecipes.text
    return render_template('GGRecipe.html')

@app.route('/Login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		session.pop('user_id', None)

		username = request.form['username']
		password = request.form['password'] 

		user = [x for x in users if x.email == username][0]
		if user and user.password == password:
			session['user_id'] = user.id
			return redirect(url_for('main'))
		return redirect(url_for('login'))
	return render_template('GGLogin.html')

@app.route('/Signup')
def signup():
    print("test")
    return render_template('GGSignup.html')

@app.route('/Contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run()
