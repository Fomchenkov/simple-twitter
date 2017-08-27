#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import sqlite3

from flask import Flask, session, redirect, render_template, request


app = Flask(__name__)
conn = sqlite3.connect('database.db')


class DataBase:
	"""
	DataBase wrapper
	"""
	def __init__(self, connection):
		self.conn = connection

	def deploy(self):
		c = self.conn.cursor()
		c.execute("""CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			login TEXT NOT NULL,
			password TEXT NOT NULL)""")
		self.conn.commit()

	def try_auth(self, login, password):
		c = self.conn.cursor()
		sql = "SELECT * FROM users"
		print("База данных:", c.execute(sql).fetchall())
		sql = f"SELECT * FROM users WHERE login='{login}' AND password='{password}'"
		print(sql)
		res = c.execute(sql).fetchone()
		print(res)
		self.conn.commit()
		if res:
			return True
		return False

	def sign_up(self, login, password):
		c = self.conn.cursor()
		sql = f"INSERT INTO users (login, password) VALUES ('{login}', '{password}')"
		print(sql)
		res = c.execute(sql)
		sql = "SELECT * FROM users"
		print("База данных:", c.execute(sql).fetchall())
		self.conn.commit()

	def close(self):
		self.conn.close()


@app.route('/', methods=['GET'])
def get_index_page():
	"""
	Redirect to user home page or redirect to signin page
	"""
	if not 'username' in session:
		return redirect('/signin')
	else:
		return redirect('/user/{!s}'.format(session['username']))


@app.route('/signin', methods=['GET'])
def get_signin_page():
	"""
	Echo sign in form
	"""
	if 'username' in session:
		return redirect('/user/{!s}'.format(session['username'])) 
	return render_template('signin.html')


@app.route('/signin', methods=['POST'])
def post_signin_page():
	"""
	Try to auth user
	"""
	login = request.form['login']
	password = request.form['password']
	db = DataBase(conn)
	if db.try_auth(login, password):
		session['username'] = login
		return redirect(f'/user/{login}')
	err_msg = 'Incorect login or password'
	return render_template('signin.html', error=err_msg)


@app.route('/signup', methods=['GET'])
def get_signup_page():
	"""
	Echo sign up form
	"""
	if 'username' in session:
		return redirect('/user/{!s}'.format(session['username'])) 
	return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def post_signup_page():
	"""
	Try register user
	"""
	login = request.form['login']
	password = request.form['password']
	password_conf = request.form['password_confirm']
	# Validate input data
	if not password == password_conf:
		err_msg = 'Passwords don\'t mathces!'
		return render_template('signup.html', error=err_msg)
	if len(login) < 4 or len(password) < 4:
		err_msg = 'Short login or password!'
		return render_template('signup.html', error=err_msg)
	db = DataBase(conn)
	db.sign_up(login, password)
	return redirect('/signin')


@app.route('/user/<username>', methods=['GET'])
def show_user_profile(username):
	"""
	Show user profile
	"""
	if not 'username' in session or not username == session['username']:
		print('pinned')
		return redirect('/')
	# Load user page
	return 'Hello, {!s}!'.format(username)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def main():
	db = DataBase(conn)
	db.deploy()
	app.secret_key = os.urandom(24)
	app.run()


if __name__ == '__main__':
	main()
