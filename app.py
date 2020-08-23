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

    result_plants = []

    res_trefle = requests.get("https://trefle.io/api/v1/plants/search?token=dsRk-kcdXoieKDbu8qVaNRIlJsrw31rYHZ0xqND0w08&q=" + str(query))
    data = res_trefle.json()["data"]

    json_result = {}
    if not data:
        # if res_trefle is null, that means we cannot get anything back from external API
        # query our own local database for the plants based on the search query
        # add the result to result_plants array
        json_result["result"] = "Oh no! There are no plants found. Give it another try!" 
        return jsonify(json_result)
    
    # if res_trefle is NOT null -> that means wer are succesfully being able to get something back from external API
    for item in data:
        print("plant_api_id: {}\ncommon_name: {}\nscientific_name: {}\nfamily: {}\nfamily_common_name: {}\ngenus: {}\nimage_url: {}\n".format(item['id'],item['common_name'],item['scientific_name'],item['family'],item['family_common_name'],item['genus'],item['image_url']))

        dbPlant = Plant(
            plant_api_id=item['id'],
            common_name=item['common_name'],
            scientific_name=item['scientific_name'],
            family=item['family'],
            family_common_name=item['family_common_name'],
            genus=item['genus'],
            image_url=item['image_url'],
        )

        # if the item does not already exists in your database, insert it
        # don't forget to take this shit out starting here
        # plant = db.session.query(Plant.plant_api_id).filter_by(plant_api_id=item['id']).first()
        # if plant is None: 
        #     db.session.add(dbPlant)
        #     db.session.commit()
        # take this shit out above

        print("*** plant", dbPlant.common_name)

        #add item to result_plants array
        result_plants.append(dbPlant.to_json())

    json_result["results"] = result_plants
    return jsonify(json_result)


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

