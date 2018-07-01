from flask import render_template, redirect, flash, url_for, request, Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateForm, ResetPasswordForm, ResetRequestForm
from flaskblog.models import User, Post
from flaskblog.users.utils import send_reset_email, save_picture
from flaskblog import db, bcrypt

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username = form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created! Login now.', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html',title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash(f'Login Unsuccessful!, Please Check Email and Passwrod', 'danger')
	return render_template('login.html',title='Login', form=form)

@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('main.home'))


@users.route("/account", methods=['GET','POST'])
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
		return redirect(url_for('users.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static',filename = 'propic/'+ current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def userpost(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username = username).first_or_404()
	posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc())\
			.paginate(per_page=5, page=page)
	return render_template('userpost.html', posts=posts, user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def resetrequest():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = ResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instruction to reset your password to you mail id', 'info')
		return redirect(url_for('users.login'))
	return render_template('resetrequest.html', title = 'Reset Password', form = form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def resettoken(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired Token!', 'warning')
		return redirect(url_for('users.resetrequest'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Your password has been changed! Login now.', 'success')
		return redirect(url_for('users.login'))
	return render_template('resettoken.html', title = 'Reset Passwored', form = form)
