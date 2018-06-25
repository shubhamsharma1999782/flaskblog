from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from personal.emailandpassword import get_email,get_pass

app = Flask(__name__)
app.config['SECRET_KEY'] ='cc822721931a1ef9af4a4a8a179ee176'
app.config['DEBUG']=True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = get_email() # Add your Email addredd here
app.config['MAIL_PASSWORD'] = get_pass() # Add your password here
mail = Mail(app)

from flaskblog import routes
