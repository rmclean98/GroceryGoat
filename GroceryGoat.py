from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/coupons')
def coupons():
    return render_template('coupons.html')

@app.route('/recipes')
def recipes():
    return render_template('recipes.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run()
