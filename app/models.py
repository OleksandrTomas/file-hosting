from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64), unique = True)
    password_hash = db.Column(db.String(72))
    admin_role = db.Column(db.Boolean) # Admin if True

    def __init__(self, name, pass_hash, admin=False):
        self.username = name
        self.password_hash = pass_hash
        self.admin_role = admin

    # add instance to db and commit
    def save(self):
        
        db.session.add(self)

        db.session.commit()

        return self


class File(db.Model):
    __tablename__='files'
    id = db.Column(db.Integer,primary_key=True)
    file_name = db.Column(db.String(64)) # original file name
    generated_name = db.Column(db.String(64), unique = True) # new generated file name
    public = db.Column(db.Boolean) 
    format = db.Column(db.String(64))
    size = db.Column(db.Float) # size in Kb
    download_count = db.Column(db.Integer)


    def __init__(self, name, generated_name, public, format, size):
        self.file_name = name
        self.generated_name = generated_name
        self.public = public
        self.format = format
        self.size = size
        self.download_count = 0

    # add instance to db and commit
    def save(self):

        db.session.add(self)

        db.session.commit()

        return self