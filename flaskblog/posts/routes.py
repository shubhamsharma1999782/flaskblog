from flask import render_template, url_for, redirect, flash, abort, request, Blueprint
from flaskblog import db
from flaskblog.models import Post
from flask_login import login_required, current_user
from flaskblog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title = form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash(f'Your post has been created. ', 'success')
		return redirect(url_for('main.home'))
	return render_template('newpost.html', title='New Post', form=form, legend = 'Create Post')

@posts.route('/post/<int:post_id>')
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)

@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
		return redirect(url_for('posts.post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('newpost.html', title = post.title, form=form, legend = 'Update Post')

@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def deletepost(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash(f'Your Post has been Deleted! ', 'success')
	return redirect(url_for('main.home'))
