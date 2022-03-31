from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import numpy as np
from datetime import datetime
import requests
import json
from passlib.hash import sha256_crypt

# Config SQL
app = Flask(__name__)
app.secret_key = 'pizzahut'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://admin:admin@localhost/pizzahut"
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80),nullable=False)
	password = db.Column(db.String(80),nullable=False)

class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	food = db.Column(db.String(80),nullable=False)
	time = db.Column(db.String(80),nullable=False)
	status = db.Column(db.String(40),nullable=False)
	foodpandaID = db.Column(db.Integer, unique=True)
	customer = db.Column(db.String(80),nullable=False)
	address = db.Column(db.String(120),nullable=False)

class RegisterForm(Form):
	username = StringField('Username', [validators.DataRequired(), validators.length(min=4, max=80)])
	password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Confirm Password')

class LoginForm(Form):
	username = StringField('Username', [validators.DataRequired()])
	password = PasswordField('Password', [validators.DataRequired()])



@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		password = sha256_crypt.hash(str(form.password.data))

		#create cursor
		
		result = User.query.filter_by(username=username).first()
		if result:
			flash("The username is registered", 'danger')
		else:
			new_user = User(username=username,password=password)
			db.session.add(new_user)
			db.session.commit()
			flash("You are now registered", 'success')
			return redirect(url_for('index'))
	return render_template('register.html', form = form)





@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		password_candidate = form.password.data

		result = User.query.filter_by(username=username).first()  

		if result:
			password = result.password

			if sha256_crypt.verify(password_candidate, password):
				session['current_user'] = {
					"username":username,
					}


				flash("Login Success", 'success')
				return redirect(url_for('index'))

			else:
				flash("PASSWORD NOT MATCHED", 'danger')
		else:
			flash('NO USER', 'danger')
	return render_template('login.html', form = form)

@app.route('/logout')
def logout():
	session.pop('current_user',None)
	return redirect(url_for('index'))

@app.route('/')
@app.route('/home', methods=['GET'])

def index():
	try:
		if session['current_user']:
			req = requests.get('http://47.242.56.77:5000/api/order')
			request_data =json.loads(req.content)
			order = Order.query.all()
			foodpandaID =[x.foodpandaID for x in Order.query.all()]
			for s in (request_data):		
				if  s['id'] in (foodpandaID):     
					pass
				else:                 
					id = s['id']
					food = s['food']
					time = s['time']
					status = s['status']
					customer = s['customer']
					address = s['address']
					new_order = Order(food=food,time=time,status=status,foodpandaID=id, customer = customer, address = address)
					db.session.add(new_order)
					db.session.commit()
			
			order = Order.query.all()
			return render_template('orderlist.html', order = order)

	except KeyError:
		flash('Please login first!','danger')
		return redirect(url_for('login'))

	return render_template('orderlist.html')



@app.route('/updatedata', methods=['POST'])
def getdata():
	req = requests.get('http://47.242.56.77:5000/api/order')
	request_data =json.loads(req.content)
	order = Order.query.all()
	foodpandaID =[x.foodpandaID for x in Order.query.all()]
	for s in (request_data):		
		if  s['id'] in (foodpandaID):     
			pass
		else:
			id = s['id']
			food = s['food']
			time = s['time']
			status = s['status']
			customer = s['customer']
			address = s['address']
			new_order = Order(food=food,time=time,status=status,foodpandaID=id, customer = customer, address = address)
			db.session.add(new_order)
			db.session.commit()
	
	order = Order.query.all()
	return jsonify('',render_template('random.html', order = order))

# @app.route('/order', methods=['GET'])
# def order():
# 	req = requests.get('http://47.242.56.77:5000/api/order')
# 	request_data =json.loads(req.content)
# 	order = Order.query.all()
# 	foodpandaID =[x.foodpandaID for x in Order.query.all()]
# 	for s in (request_data):		
# 		if  s['id'] in (foodpandaID):     
# 			pass
# 		else:                 
# 			id = s['id']
# 			food = s['food']
# 			time = s['time']
# 			status = s['status']
# 			customer = s['customer']
# 			address = s['address']
# 			new_order = Order(food=food,time=time,status=status,foodpandaID=id, customer = customer, address = address)
# 			db.session.add(new_order)
# 			db.session.commit()
# 	order = Order.query.all()
# 	return render_template('orderlist.html', order = order)

	
	# id = request_data['id']
	# food = request_data['food']
	# time = request_data['time']
	# status = request_data['status']
	# customer = request_data['customer']
	# address = request_data['address']
	# new_order = Order(food=food,time=time,status=status,foodpandaID=id, customer = customer, address = address)
	# db.session.add(new_order)
	# db.session.commit()
	# order = Order.query.all()
	# return render_template('orderlist.html', order = order)
	
	

@app.route('/send/<int:id>/')
def send(id):

	api_url = 'http://localhost:5000/compelete'
	Order.query.filter_by(id=id).update({Order.status: "Compelete"})
	order = Order.query.filter_by(id=id).first()
	db.session.commit()
	update = {
		'id': order.foodpandaID,
		'status':order.status
	}
	r = requests.post(url=api_url, json=update)
	
	return redirect(url_for('index'))







if __name__ == '__main__':
	db.create_all()
	app.run(debug = True, port=4000, host='0.0.0.0')