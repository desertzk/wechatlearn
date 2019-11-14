from .context import db
import enum
import os
from datetime import datetime


class GenderType(enum.Enum):
    male =1
    female = 0


class User(db.Model):
    __tablename__ = 'tusers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    email = db.Column(db.String(128), index=True, unique=True)
    birthday = db.Column(db.String(16))
    height = db.Column(db.DECIMAL(5,2))
    weight = db.Column(db.DECIMAL(5,2))
    gender=db.Column(db.Integer)
    role=db.Column(db.Integer)
    identity_id=db.Column(db.String(32), unique=True)
    open_id= db.Column(db.String(32))
    city = db.Column(db.String(16))
    province = db.Column(db.String(16))
    status = db.Column(db.Integer)


    def __repr__(self):
        return '<User {}>'.format(self.username)


class Daytimecheckdata(db.Model):
    __tablename__ = 'tdaytimecheckdata'
    diastolic_pressure = db.Column(db.Integer)
    systolic_pressure = db.Column(db.Integer)
    rhythm_of_heart = db.Column(db.Integer)
    medicines_list = db.Column(db.String(256))
   # visit_time = db.Column(db.Integer)
   # triglyceride = db.Column(db.DECIMAL(10,2))
   # total_cholesterol=db.Column(db.DECIMAL(10,2))
   # hdl_c=db.Column(db.DECIMAL(10,2))
   # ldl_c=db.Column(db.DECIMAL(10,2))
    identity_id=db.Column(db.String(32), primary_key=True)
   # BNP = db.Column(db.DECIMAL(10,2))
   # creatinine = db.Column(db.DECIMAL(10,2))
    datetime = db.Column(db.Date,default=datetime.today().strftime("%Y-%m-%d"),primary_key=True)


    def __repr__(self):
        return '<User {}>'.format(self.username)
