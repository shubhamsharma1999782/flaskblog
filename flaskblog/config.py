from personal.emailandpassword import get_email,get_pass

class Config:
    SECRET_KEY ='cc822721931a1ef9af4a4a8a179ee176'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    DEBUG=True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = get_email() # Add your Email addredd here
    MAIL_PASSWORD = get_pass() # Add your password here