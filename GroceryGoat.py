from flask import Flask, render_template, request, session, redirect, url_for
import os

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

print(users)

app = Flask(__name__)
app.secret_key = 'tempsecretkey'

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

@app.route('/')
def main():
    Floating_shopping = os.path.join(app.config['IMAGE_FOLDER'], 'Floating_shopping_list.png')
    recipe_template = os.path.join(app.config['IMAGE_FOLDER'], 'recipe_template.png')
    return render_template('GGHome.html', home_shopping_image = Floating_shopping, home_recipe_image = recipe_template)

@app.route('/Lists')
def coupons():
    print("Lists pressed")
    return render_template('GGLists.html')

@app.route('/Recipes')
def recipes():
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
