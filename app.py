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

	def login_exists(self, login):
		c = self.conn.cursor()
		sql = f"SELECT * FROM users WHERE login='{login}'"
		res = c.execute(sql).fetchone()
		self.conn.commit()
		print(res)
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
		# Create table for this user posts
		sql = f"""CREATE TABLE IF NOT EXISTS user_{login} (
			id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			text TEXT NOT NULL)"""
		print(sql)
		c.execute(sql)
		self.conn.commit()

	def add_new_post(self, login, text):
		c = self.conn.cursor()
		sql = f"INSERT INTO user_{login} (text) VALUES ('{text}')"
		print(sql)
		c.execute(sql)
		self.conn.commit()

	def get_post(self, login, post_id):
		c = self.conn.cursor()
		sql = f"SELECT * FROM user_{login} WHERE id='{post_id}'"
		print(sql)
		res = c.execute(sql).fetchone()
		print(res)
		self.conn.commit()
		if not res:
			return None
		return {
			'id': res[0],
			'text': res[1]
		}

	def get_all_posts(self, login):
		c = self.conn.cursor()
		sql = f"SELECT * FROM user_{login} ORDER BY id DESC"
		print(sql)
		res = c.execute(sql)
		print(res)
		posts = []
		for post in res:
			posts.append({
				'id': post[0],
				'text': post[1]
			})
		print(posts)
		return posts

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
	if db.login_exists(login):
		err_msg = 'This login is exists!'
		return render_template('signup.html', error=err_msg)
	db.sign_up(login, password)
	return redirect('/signin')


@app.route('/user/<username>', methods=['GET'])
def show_user_profile(username):
	"""
	Show user profile
	"""
	if not 'username' in session or not username == session['username']:
		return redirect('/')
	post_id = request.args.get('post_id')
	db = DataBase(conn)
	if post_id:
		print('Page redirect', post_id)
		post = db.get_post(username, post_id)
		if not post:
			return render_template('404.html'), 404
		return render_template('view_post.html', post=post)
	posts = db.get_all_posts(username)
	if len(posts) == 0:
		msg = 'No posts anywhere!'
		return render_template('no_posts.html', username=username, message=msg)
	return render_template('posts.html', username=username, posts=posts)


@app.route('/new_post', methods=['GET'])
def get_new_post():
	if not 'username' in session:
		return redirect('/')
	return render_template('new_post.html')


@app.route('/new_post', methods=['POST'])
def post_new_post():
	if not 'username' in session:
		return redirect('/')
	text = request.form['text']
	print(text)
	db = DataBase(conn)
	db.add_new_post(session['username'], text)
	return redirect('/')


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
