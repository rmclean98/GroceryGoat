from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('GGHome.html')

@app.route('/Lists')
def coupons():
    return render_template('GGLists.html')

@app.route('/Recipes')
def recipes():
    return render_template('GGRecipe.html')

@app.route('/Login')
def login():
    return render_template('GGLogin.html')

if __name__ == '__main__':
    app.run()
