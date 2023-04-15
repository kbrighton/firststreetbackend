import os
basedir = os.path.abspath(os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'thisisatestthing'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    BOOTSTRAP_BOOTSWATCH_THEME = 'lumen'
    WTF_CSRF_CHECK_DEFAULT = False



class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
