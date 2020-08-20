import os 
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Plant, ProgressJournal, UserPlant, PlantJournal

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///brown_thumb'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "br0wnthumbs")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route("/test", methods=["GET"])
def test():
    return ("WORKS")

@app.route("/users/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup."""

    

    return ("WORKS")