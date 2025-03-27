from flask import render_template, Blueprint

import markdown

from app.models import Post

bp = Blueprint('main', __name__)

marker = '<!-- more -->'

@bp.route('/')
@bp.route('/index')
def index():
    posts_from_db = Post.query.order_by(Post.timestamp.desc()).all()
    posts_for_template = []
    preview_length = 300

    for post in posts_from_db:
        content = post.markdown_content
        preview_html = None

        if content:
            if marker in content:
                preview_md = content.split(marker, 1)[0]
                preview_html = markdown.markdown(preview_md, extensions=['fenced_code', 'tables'])
            else:
                truncated_md = content[:preview_length]
                if len(content) > preview_length:
                    last_space = truncated_md.rfind(' ')
                    if last_space > preview_length * 0.8:
                        truncated_md = truncated_md[:last_space]
                    truncated_md += "..."

                preview_html = markdown.markdown(truncated_md, extensions=['fenced_code', 'tables'])

        post_data = {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'timestamp': post.timestamp,
            'preview_html': preview_html
        }
        posts_for_template.append(post_data)

    return render_template('index.html', title='Главная', posts=posts_for_template)

@bp.route('/post/<slug>')
def view_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    html_content = None

    if post.markdown_content:
         full_content_md = post.markdown_content.replace(marker, '', 1)
         html_content = markdown.markdown(full_content_md, extensions=['fenced_code', 'tables'])

    return render_template('post_view.html', title=post.title, post=post, content=html_content)