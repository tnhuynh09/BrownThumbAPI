import os 
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import re
import requests
# from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Plant, ProgressJournal, UserPlant, PlantJournal

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///brown_thumb'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "br0wnthumbs")
# toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.route("/test", methods=["GET"])
def test():
    return ("WORKS")

@app.route("/search", methods=["GET"])
@cross_origin()
def search():
    query = request.args["query"]
    # res_num = requests.get("http://numbersapi.com/" + str(r) + "/trivia")
    res_trefle = requests.get("https://trefle.io/api/v1/plants/search?token=dsRk-kcdXoieKDbu8qVaNRIlJsrw31rYHZ0xqND0w08&q=" + str(query))
    # print("res_trefle ", res_trefle.text)
    return jsonify(res_trefle.text)

@app.route("/users/signup", methods=["POST"])
@cross_origin()
def signup():
    """Handle user signup."""

    username = request.json["username"]
    password = request.json["password"]
    image_url = request.json["imageUrl"]
    
    json_result = {}

    username_errors = []
    if not username: 
        username_errors.append("This field is required.")
    elif len(str(username)) < 7:
        username_errors.append("Username must have at least 6 characters.")

    password_errors = []
    if not password: 
        password_errors.append("This field is required.")
    elif len(str(password)) < 7:
        password_errors.append("Password must have at least 6 characters.")

    if not image_url:
        image_url = "/static/images/default-pic.png"

    json_errors = {}

    if len(username_errors) > 0:
        json_errors["username"] = username_errors

    if len(password_errors) > 0:
        json_errors["password"] = password_errors
    
    if json_errors:
        json_result["errors"] = json_errors
        return (jsonify(json_result))
    
    else:
        user = User.signup(username, password, image_url)
        if user == None:
            username_errors.append("This username already exist. Please try another.")
            json_errors["username"] = username_errors
            json_result["errors"] = json_errors
        else:
            json_result["user"] = user.to_json()

        return jsonify(json_result)

@app.route("/users/login", methods=["POST"])
@cross_origin()
def login():
    """Handle user login."""

    username = request.json["username"]
    password = request.json["password"]

    user = User.authenticate(username, password)

    json_result = {}

    if not user: 
        json_errors = {}
        json_errors["errors"] = "Username and password does not match. Please try again."
        json_result["errors"] = json_errors

    else:
        json_result["user"] = user.to_json()

    return jsonify(json_result)

