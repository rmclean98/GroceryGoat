from flask_sqlalchemy import SQLAlchemy
from __main__ import app

db = SQLAlchemy(app)

class Users(db.Model):
	__tablename__ = 'Users'
	userId = db.Column(db.Integer, primary_key=True, nullable=False)    
	emailId = db.Column(db.String(50), unique = True, nullable=False)    
	password = db.Column(db.String(16), nullable=False)
	fname = db.Column(db.String(50), nullable=False)     
	lname = db.Column(db.String(50), nullable=False)  


class ListDetails(db.Model):
	__tablename__ = 'ListDetails'
	listId = db.Column(db.Integer, primary_key=True,nullable=False)
	listTitle = db.Column(db.String(300), nullable=False)
	adDescription = db.Column(db.String(3500), nullable=False)


class GroceryLists(db.Model):
	__tablename__ = 'GroceryLists'
	groceryListsId = db.Column(db.Integer, primary_key=True, nullable=False)
	listId = db.Column(db.Integer, db.ForeignKey('ListDetails.listId'))
	userId = db.Column(db.Integer, db.ForeignKey('Users.userId'))

    


    



    
