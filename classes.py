from flask.ext.wtf import Form
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class newPost(Form):
    title = StringField('title', validators=[DataRequired()])
    summary = StringField('summary', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])
    author = StringField('author', validators=[DataRequired()], default="Reuben")
    page_type = SelectField('page_type', choices=[('blog', 'Blog'), ('making', 'Making')], validators=[DataRequired()])