from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm

class OtpForm(FlaskForm):
    otp = StringField('Код из Telegram', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Подтвердить')

class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=140)])
    markdown_content = TextAreaField('Текст поста (Markdown)')
    post_image = FileField('Изображение для поста', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')
    ])
    submit = SubmitField('Сохранить пост')