from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm

class OtpForm(FlaskForm):
    otp = StringField('The code from telegram', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Sumbit')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=140)])
    markdown_content = TextAreaField('Text of post (Markdown)')
    post_image = FileField('Image for post', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image!')
    ])
    submit = SubmitField('Save a post')