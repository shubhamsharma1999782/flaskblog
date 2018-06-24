from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] ='cc822721931a1ef9af4a4a8a179ee176'
app.config['DEBUG']=True
#host = 'shubham199782.mysql.pythonanywhere-services.com'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
from flaskblog import routes
