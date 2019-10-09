from .context import db
import enum

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
    id = db.Column(db.Integer, primary_key=True)
    blood_pressure = db.Column(db.Integer)
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