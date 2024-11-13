import os

from dotenv import load_dotenv

# load environment from .env file
load_dotenv()

class Config(object):
    DEBUG = True
    
    DEVELOPMENT = True

    SECRET_KEY = os.getenv('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.getenv('DATABASE_URI') + '.sqlite'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # upload folder location
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__)+"/../", 'Uploads'))
    
    # max size of files
    MAX_CONTENT_LENGTH = 100 * 1000 * 1000  # 100 MB