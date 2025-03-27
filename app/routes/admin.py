import os
from flask import render_template, flash, redirect, url_for, request, Blueprint, current_app
from flask_login import login_required
from app import db
from app.forms import PostForm
from app.models import Post
from app.utils import save_picture, generate_slug
from app.decorators import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/posts')
@admin_required
def list_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('admin/posts_list.html', title='Управление постами', posts=posts)

@bp.route('/new_post', methods=['GET', 'POST'])
@admin_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        slug = generate_slug(form.title.data)
        if Post.query.filter_by(slug=slug).first():
             flash('Пост с таким заголовком (и slug) уже существует!', 'danger')
             return render_template('admin/post_form.html', title='Новый пост', form=form, legend='Новый пост')

        image_file = None
        if form.post_image.data:
            image_file = save_picture(form.post_image.data)

        post = Post(title=form.title.data,
                    slug=slug,
                    markdown_content=form.markdown_content.data,
                    image_filename=image_file)
        db.session.add(post)
        db.session.commit()
        flash('Пост успешно создан!', 'success')
        return redirect(url_for('admin.list_posts'))
    return render_template('admin/post_form.html', title='Новый пост', form=form, legend='Новый пост')


@bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        new_slug = generate_slug(form.title.data)
        if new_slug != post.slug and Post.query.filter_by(slug=new_slug).first():
            flash('Пост с таким новым заголовком (и slug) уже существует!', 'danger')
            return render_template('admin/post_form.html', title='Редактировать пост', form=form, legend='Редактировать пост')

        post.title = form.title.data
        post.slug = new_slug
        post.markdown_content = form.markdown_content.data
        if form.post_image.data:
             if post.image_filename:
                 try:
                     os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_filename))
                 except OSError:
                     pass
             post.image_filename = save_picture(form.post_image.data)

        db.session.commit()
        flash('Пост успешно обновлен!', 'success')
        return redirect(url_for('admin.list_posts'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.markdown_content.data = post.markdown_content
    return render_template('admin/post_form.html', title='Редактировать пост',
                           form=form, legend='Редактировать пост', current_image=post.image_filename)


@bp.route('/delete_post/<int:post_id>', methods=['POST'])
@admin_required
def delete_post(post_id):
     post = Post.query.get_or_404(post_id)
     if post.image_filename:
         try:
             os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], post.image_filename))
         except OSError:
             pass
     db.session.delete(post)
     db.session.commit()
     flash('Пост удален.', 'success')
     return redirect(url_for('admin.list_posts'))