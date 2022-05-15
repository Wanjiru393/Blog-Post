from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)
app.config['SECRET_KEY'] = 'a3033383788d53fac524640f4e3f3070'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///site.db'      
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'



from app import views