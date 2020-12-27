class Config(object):
    # base config
    SECRET_KEY = 'z2v(bgmv3nsbd3fc7tb+up_4)xsey4ka=%$fp4kpaz&=(4b0@h'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


class DevConfig(Config):
    # Configs during development
    DEBUG=True
    TESTING = True
    # SQLAlchemy configs
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://paul:00!FrozeN!00@localhost/survey'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
