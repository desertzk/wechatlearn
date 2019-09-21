from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,HiddenField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired()])
    identification = StringField('身份证', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    wxopenid=HiddenField()
    sex=HiddenField()
    # password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    submit = SubmitField('提交')