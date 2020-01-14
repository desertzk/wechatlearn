# coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,IntegerField,DecimalField, SubmitField,HiddenField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired()])
    identification = StringField('身份证', validators=[DataRequired()])
    email = StringField('email')
    wxopenid=HiddenField()
    json_user_info=""
    sex=HiddenField()
    # password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    submit = SubmitField('提交')


class DailyCheckForm(FlaskForm):
    identification = StringField('身份证', validators=[DataRequired()])

    diastolic_pressure = IntegerField('舒张压')
    systolic_pressure = IntegerField('收缩压')
    rhythm_of_heart = IntegerField('心率')
    medicines_list = StringField('药物清单')
    #visit_time = IntegerField('随访时间')
    #triglyceride = DecimalField('甘油三酸酯')
    #total_cholesterol = DecimalField('总胆固醇')
    #hdl_c = DecimalField('高密度脂蛋白胆固醇')
    #ldl_c = DecimalField('低密度脂蛋白胆固醇')
    #BNP = DecimalField('BNP')
    #creatinine = DecimalField('肌酐')


    # password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    submit = SubmitField('提交')


class WeightRecordForm(FlaskForm):
    weight = DecimalField('体重')
    submit = SubmitField('提交')


class BloodPressureRecordForm(FlaskForm):
    diastolic_pressure = IntegerField('舒张压')
    systolic_pressure = IntegerField('收缩压')
    submit = SubmitField('提交')


class HeartRateRecordForm(FlaskForm):
    rhythm_of_heart = IntegerField('心率')
    submit = SubmitField('提交')


class MedicineForm(FlaskForm):
    medicines_list = StringField('药物清单')
    submit = SubmitField('提交')




# class RegisterForm(FlaskForm):
#     name = StringField('姓名', validators=[DataRequired()])
#     identification = StringField('身份证', validators=[DataRequired()])
#     email = StringField('email', validators=[DataRequired()])
#     wxopenid=HiddenField()
#     json_user_info=""
#     sex=HiddenField()
#     # password = PasswordField('Password', validators=[DataRequired()])
#     # remember_me = BooleanField('Remember Me')
#     submit = SubmitField('提交')
