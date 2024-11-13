import os, logging

# import modules from python packages
from flask              import Flask
from flask_sqlalchemy   import SQLAlchemy
from flask_login        import LoginManager
from flask_bcrypt       import Bcrypt
from flask_wtf          import CSRFProtect 

app = Flask(__name__)

# config app form file
app.config.from_object('app.config.Config')

# create folder for uploads if not exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

# initialize all parts of app
db = SQLAlchemy(app)

bc = Bcrypt(app)

lm = LoginManager()
lm.init_app(app)

csrf = CSRFProtect(app) 

from app import views, models

# create tables in db 
with app.app_context():
    db.create_all()
