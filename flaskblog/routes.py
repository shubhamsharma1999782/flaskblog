import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateForm, PostForm, ResetRequestForm, ResetPasswordForm
from flaskblog.models import User, Post
from flaskblog import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
	return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html',title = 'About')

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username = form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created! Login now.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html',title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash(f'Login Unsuccessful!, Please Check Email and Passwrod', 'danger')
	return render_template('login.html',title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_,f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/propic', picture_fn)

	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
	form = UpdateForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your Account info is Updated successfully','success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static',filename = 'propic/'+ current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title = form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash(f'Your post has been created. ', 'success')
		return redirect(url_for('home'))
	return render_template('newpost.html', title='New Post', form=form, legend = 'Create Post')

@app.route('/post/<int:post_id>')
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def updatepost(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash(f'Your Post has been Updated! ', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('newpost.html', title = post.title, form=form, legend = 'Update Post')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def deletepost(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash(f'Your Post has been Deleted! ', 'success')
	return redirect(url_for('home'))

@app.route("/user/<string:username>")
def userpost(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username = username).first_or_404()
	posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc())\
			.paginate(per_page=5, page=page)
	return render_template('userpost.html', posts=posts, user=user)

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='flaskblog@demo.com',
										recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('resettoken', token=token, _external = True)}

If you did not make this request then simply ignore this and no changes will be made.
'''
	mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def resetrequest():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = ResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instruction to reset your password to you mail id', 'info')
		return redirect(url_for('login'))
	return render_template('resetrequest.html', title = 'Reset Password', form = form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def resettoken(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired Token!', 'warning')
		return redirect(url_for('resetrequest'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Your password has been changed! Login now.', 'success')
		return redirect(url_for('login'))
	return render_template('resettoken.html', title = 'Reset Passwored', form = form)
