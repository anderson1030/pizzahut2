from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from flask_admin.form.upload import ImageUploadField

# Config SQL
app = Flask(__name__)
app.secret_key = 'Pizzahut'
app.config["SQLALCHEMY_DATABASE_URI"] = ""


@app.route('/')
@app.route('/home')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/order', methods=['POST'])
def order():
	request_data = request.get_json(force=True)
	id = request_data['id']
	time = request_data['time']
	status = request_data['prepare']
	return redirect(url_for('index'))


	






if __name__ == '__main__':
	#db.create_all()
	app.run(debug = True, port=4000)