from flask import Flask, render_template, request, session, redirect,flash

# from werkzeug import secure_filename

import json
import os
import math
from datetime import datetime
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import htmlentities
from bson.objectid import ObjectId

client = MongoClient('mongodb+srv://shivamsatyam:shivamsatyam123@cluster0.hrigk.mongodb.net/flask_blog?retryWrites=true&m=majority')
database = client['flask_blog']

app = Flask(__name__)
app.secret_key = 'super-secret-key'
bcrypt = Bcrypt()

@app.route('/')
def home():
	posts = database.data.find()
	return render_template('index.html',posts=posts,username=session["username"])

@app.route('/signin', methods = ['GET', 'POST'])
def siginIn():
	if (request.method=="POST"):
		username = request.form.get('name')
		password = request.form.get('password')
		email = request.form.get('email')

		
		password_hash = bcrypt.generate_password_hash(str(password))

		no_of_user = database.person.count({"username":str(username)})
		no_of_email = database.person.count({"email":str(email)})

		if no_of_user!=0:
			flash("The username already exist","danger")
		elif no_of_email!=0:
			flash("The email id is taken ","info")	
		else:
			record_data = {
			"username":htmlentities.encode(username),
			"email":email,
			"password":password_hash
			}
			database.person.insert_one(record_data)
			
			return redirect('/')	

	return render_template('signin.html')

@app.route('/login',methods=['GET','POST'])
def login():
	if (request.method=="POST"):
		username = request.form.get('name')
		password = request.form.get('password')

		for item in database.person.find({"username":username}):
			if item["username"] != username:
				flash("Invalid Login details","danger")
			elif not bcrypt.check_password_hash(item['password'],password):	
				flash("Invalid bcrypt password hashing details","warn")
			else:
				flash("Session is created")
				session['username'] = username
				session['email'] = item['email']	

	return render_template('login.html') 



@app.route('/post',methods=["GET","POST"])
def post():

	if request.method=="POST":
		submit_data = {
		"username":htmlentities.encode(session['username']),
		"email":session['email'],
		"topic":htmlentities.encode(request.form.get('topic')),
		"content":request.form.get('content'),
		"views":0
		}

		database.data.insert_one(submit_data)
		return redirect('/')
	
	if ("username" in session):	
		return render_template('post.html')
	else:
		return redirect('/')	


@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('email')

	return redirect('/')


@app.route('/show/<string:id>')
def show(id):
	data = database.data.find_one({"_id":ObjectId(id)})
	return render_template('show.html',data=data,username=session['username'])



@app.route('/your')
def your():
	if ('username' in session):
		data = database.data.find({"username":session['username']})
		return render_template('your.html',data=data,user=session['username'])

	return redirect('/')
		
app.run(debug=True)
