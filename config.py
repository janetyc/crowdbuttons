import os

class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = ""
    DB_USER = ""
    DB_PASS = ""
    DB_NAME = "crowdBt"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.getenv("MONGOHQ_URL")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
