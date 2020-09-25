import os 
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_swagger_ui import get_swaggerui_blueprint
import re
import requests
import jwt
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

JWT_SECRET = app.config['SECRET_KEY']
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 86400

connect_db(app)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "brown-thumb-api"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###

@app.route("/search", methods=["GET"])
@cross_origin()
def search():
    """Handle search."""
    
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
        
        dbPlant = Plant(
            plant_api_id=item['id'],
            common_name=item['common_name'],
            scientific_name=item['scientific_name'],
            family=item['family'],
            family_common_name=item['family_common_name'],
            genus=item['genus'],
            image_url=item['image_url'],
        )

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
        image_url = "http://brown-thumb-api.herokuapp.com/static/images/profile-default.png"

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
            jwt_token = jwt.encode(user.to_json(), JWT_SECRET, JWT_ALGORITHM)
            json_result["jwt"] = jwt_token.decode('utf-8')

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
        jwt_token = jwt.encode(user.to_json(), JWT_SECRET, JWT_ALGORITHM)
        json_result["jwt"] = jwt_token.decode('utf-8')

    return jsonify(json_result)

@app.route("/users/edit", methods=["PATCH"])
@cross_origin()
def edit_user():
    """Handle user profile edit."""

    user_id = request.json["userId"]
    new_image_url = request.json["imageUrl"]

    # decode JWT here
    # Check to see if user_id is equal to the decode_jwt_user_id
    # if they don't match, return an error or something

    jwt_user = decode_jwt(request)
    if int(user_id) is not jwt_user["id"]:
        return jsonify({"error": "Unauthorized"})

    if not new_image_url:
        new_image_url = "http://brown-thumb-api.herokuapp.com/static/images/profile-default.png"

    user = User.query.get_or_404(user_id)

    db.session.query(User).filter_by(id=user_id).update({User.image_url: new_image_url})

    db.session.add(user)
    db.session.commit()

    json_result = {}
    json_result["user"] = user.to_json()
    
    return jsonify(json_result)

@app.route("/plants", methods=["POST"])
@cross_origin()
def add_plants():
    """Adding plants to users_plants table."""

    user_id = request.json["userId"]
    plant_api_id = request.json["plantApiId"]
    common_name = request.json["commonName"]
    scientific_name = request.json["scientificName"]
    family = request.json["family"]
    family_common_name = request.json["familyCommonName"]
    genus = request.json["genus"]
    image_url = request.json["imageUrl"]

    # decode JWT here
    # Check to see if user_id is equal to the decode_jwt_user_id
    # if they don't match, return an error or something

    jwt_user = decode_jwt(request)
    if int(user_id) is not jwt_user["id"]:
        return jsonify({"error": "Unauthorized"})
    
    dbPlant = Plant(
        plant_api_id=plant_api_id,
        common_name=common_name,
        scientific_name=scientific_name,
        family=family,
        family_common_name=family_common_name,
        genus=genus,
        image_url=image_url,
    )

    plant = db.session.query(Plant.plant_api_id).filter_by(plant_api_id=plant_api_id).first()

    if plant is None: 
        db.session.add(dbPlant)
        db.session.commit()
    
    plant = Plant.query.filter_by(plant_api_id=dbPlant.plant_api_id).first()
    plant_id = plant.id 

    dbUsersPlants = UserPlant(
        user_id=user_id,
        plant_id=plant_id,
    )

    db.session.add(dbUsersPlants)
    db.session.commit()

    json_result = {}
    new_plant = {}
    new_plant["userId"] = user_id
    new_plant["plantId"] = plant_id
    json_result["usersPlant"] = new_plant

    return jsonify(json_result)

@app.route("/plants/<int:user_plant_id>", methods=["GET"])
@cross_origin()
def get_user_plant(user_plant_id):
    """Get a single user_plant."""

    user_plant = UserPlant.query.get(user_plant_id)

    # decode JWT
    # check if user_plant.user_id is the same as jwt user id
    # if not return error

    jwt_user = decode_jwt(request)
    if int(user_plant.user_id) is not jwt_user["id"]:
        return jsonify({"error": "Unauthorized"})

    plant = Plant.query.get(user_plant.plant_id)

    json_result = {}
    json_result["result"] = plant.to_json()

    return jsonify(json_result)

@app.route("/plants/<int:user_plant_id>", methods=["DELETE"])
@cross_origin()
def delete_user_plants(user_plant_id):
    """Deleting plant from user's account."""

    user_plant = UserPlant.query.get(user_plant_id)
    # decode JWT
    # check if user_plant.user_id is the same as jwt user id
    # if not return error

    jwt_user = decode_jwt(request)
    if int(user_plant.user_id) is not jwt_user["id"]:
        return jsonify({"error": "Unauthorized"})

    db.session.delete(user_plant)
    db.session.commit()

    json_result = {}
    delete_message = {}
    delete_message["message"] = "successfully removed plant"
    json_result["result"] = delete_message

    return jsonify(json_result)

@app.route("/plants/user/<int:user_id>", methods=["GET"])
@cross_origin()
def show_user_plants(user_id):
    """Show all plants user added."""

    # decode JWT
    # check if user_id is the same as jwt user id
    # if not return error
    # print("show_user_plants user_id", request.headers["Authorization"])

    jwt_user = decode_jwt(request)
    if int(user_id) is not jwt_user["id"]:
        return jsonify({"error": "Unauthorized"})

    user = User.query.get_or_404(user_id)
    users_plants = UserPlant.query.filter_by(user_id=user_id).all()

    json_result = {}
    result_plants = []

    for user_plant in users_plants:
        plant = Plant.query.get(user_plant.plant_id)
        modified_plant = plant.to_json()
        modified_plant["user_plant_id"] = user_plant.id

        result_plants.append(modified_plant)
    
    json_result["results"] = result_plants
    return jsonify(json_result)

@app.route("/plants/<int:user_plant_id>/journal", methods=["POST"])
@cross_origin()
def add_plant_journal(user_plant_id):
    """Add a journal to a plant."""
    user_plant = UserPlant.query.get(user_plant_id)
    # decode JWT
    # check if user_plant.user_id is the same as jwt user id
    # if not return error

    jwt_user = decode_jwt(request)
    if int(user_plant.user_id) is not jwt_user["id"]:
        return jsonify({"error": "Unauthorized"})


    title = request.json["title"]
    image_url = request.json["imageUrl"]
    notes = request.json["notes"]

    if not image_url:
        image_url = "http://brown-thumb-api.herokuapp.com/static/images/journal-default.jpeg"
    
    dbProgressJournal = ProgressJournal(
        title=title,
        image_url=image_url,
        notes=notes,
    )

    db.session.add(dbProgressJournal)
    db.session.commit()

    progressJournal = ProgressJournal.query.filter_by(id=dbProgressJournal.id).first()

    dbPlantJournal = PlantJournal(
        user_plant_id=user_plant_id,
        journal_id=progressJournal.id,
    )

    db.session.add(dbPlantJournal)
    db.session.commit()

    json_result = {}
    message = {}
    message["message"] = "journal successfully added"
    json_result["result"] = message

    return jsonify(json_result)

@app.route("/plants/<int:user_plant_id>/journal", methods=["GET"])
@cross_origin()
def show_plant_journals(user_plant_id):
    """Show all journals of a plant."""

    user_plant = UserPlant.query.get_or_404(user_plant_id)
    # decode JWT
    # check if user_plant.user_id is the same as jwt user id
    # if not return error

    # jwt_user = decode_jwt(request)
    # if user_plant.user_id is not jwt_user["id"]:
    #     return jsonify({"error": "Unauthorized"})

    plants_journals = PlantJournal.query.filter_by(user_plant_id=user_plant_id).all()

    json_result = {}
    result_journals = []
    
    for plant_journal in plants_journals:
        journal = ProgressJournal.query.get(plant_journal.journal_id)
        journal = journal.to_json()

        result_journals.append(journal)
    
    json_result["results"] = result_journals
    return jsonify(json_result)

@app.route("/plants/<int:plant_journal_id>/journal", methods=["DELETE"])
@cross_origin()
def delete_plant_journals(plant_journal_id):
    """Deleting a journal from a user's plant."""

    plant_journal = PlantJournal.query.get(plant_journal_id)

    # decode JWT
    # get user_plant from plant_journal.user_plant_id
    # check if user_plant.user_id is the same as jwt user id
    # if not return error
    user_plant = UserPlant.query.get_or_404(plant_journal.user_plant_id)
    jwt_user = decode_jwt(request)
    if int(user_plant.user_id) is not jwt_user["id"]:
        return jsonify({"error": "Unauthorized"})

    progress_journal = ProgressJournal.query.get(plant_journal.journal_id)

    db.session.delete(plant_journal)
    db.session.commit()

    db.session.delete(progress_journal)
    db.session.commit()

    json_result = {}
    delete_message = {}
    delete_message["message"] = "successfully removed journal"
    json_result["result"] = delete_message

    return jsonify(json_result)

def decode_jwt(request):
    jwt_token = request.headers["Authorization"]
    user = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return user