from flask import Flask, render_template
import os

IMAGE_FOLDER = os.path.join('static', 'images')

app = Flask(__name__)


app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

@app.route('/')
def main():
    Floating_shopping = os.path.join(app.config['IMAGE_FOLDER'], 'Floating_shopping_list.png')
    recipe_template = os.path.join(app.config['IMAGE_FOLDER'], 'recipe_template.png')
    return render_template('GGHome.html', home_shopping_image = Floating_shopping, home_recipe_image = recipe_template)

@app.route('/Lists')
def coupons():
    return render_template('GGLists.html')

@app.route('/Recipes')
def recipes():
    return render_template('GGRecipe.html')

@app.route('/Login')
def login():
    return render_template('GGLogin.html')

@app.route('/Signup')
def signup():
    return render_template('GGSignup.html')

if __name__ == '__main__':
    app.run()
