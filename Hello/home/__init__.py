from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo

app=Flask(__name__,template_folder='templates')

app.config['SECRET_KEY']='f0f636a7209e2de0e0ab5c1347554459'
app.config['SQLALCHEMY_DATABASE_URI']="postgresql://dhanya:tarasusan@localhost:5432/register"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['MONGO_URI']='mongodb://localhost:27017/authentication'

mongo=PyMongo(app)
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

from home import routes