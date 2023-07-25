
import os
class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    SECRET_KEY = os.getenv("SECRET_KEY")
    OPENAI_KEY = os.getenv("OPENAI_KEY")

config = {
    'development': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'production': DevelopmentConfig
}
