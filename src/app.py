"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Character, Gender, Specie, Season, Episode, User
# Es de la compania que hizo flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import re
# generate_password_hash un string que nosostros creemos 
# check_password_hash(abc1234, lakjsdfhasiudfbasdflkaj) -> True o False
# Bcrypt

PASSWORD_REGEX = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}"

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Una firma
app.config['JWT_SECRET_KEY'] = os.environ.get("FLASK_APP_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600 # 1 hora en segundos

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#CRUD
# Vamos a crear un modelo usuario
# Vamos a crear 2 endpoints para ese usuario
#   1. Register/Signup
#   2. Login/Signin
# Prevenir que alguien sin una sesion creada
# Pueda crear personajes/episodios/temporadas
# Los usuarios sin sesion solo podran hacer metodos get


# AUTH
@app.route('/register', methods=["POST"])
def user_register():
    try:
        body = request.json
        email = body.get("email", None)
        password = body.get("password", None)
        if email is None or password is None:
            return jsonify({"error": "Email and password required"}), 400
        
        email_is_taken = User.query.filter_by(email=email).first()
        if email_is_taken:
            return jsonify({"error": "Email already in use"}), 400
        # if not re.search(PASSWORD_REGEX, password):
        #     return jsonify({"error": "la contrasenia.........."}), 404
        password_hash = generate_password_hash(password)
        print(password_hash, len(password_hash))
        # Debemos encriptar esa contrasenia
        user = User(email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User created"}), 201


    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        body = request.json
        email = body.get("email", None)
        password = body.get("password", None)
        if email is None or password is None:
            return jsonify({"error": "password and email required"}), 400
        
        user = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"error": "Email or password wrong"}), 404
        
        if not check_password_hash(user.password, password):               
            return jsonify({"error": "Email or password wrong"}), 400
        
        
        auth_token = create_access_token({"id": user.id, "email": user.email})
        return jsonify({"token": auth_token}), 200
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

# la informacion que tenemos en el token
@app.route("/me", methods=["GET"])
@jwt_required()
def get_user_data():
    user_data = get_jwt_identity()
    return jsonify(user_data), 200
# RICK AND MORTY

@app.route('/characters', methods=["GET"])
def get_characters():
    characters = Character.query.all()
    serialized_characters = [character.serialize() for character in characters]
    return jsonify({"characters": serialized_characters})

@app.route("/character", methods=["POST"])
@jwt_required() # Este endpoint necesita un token
def create_character():
    body = request.json

    name = body.get("name", None)
    gender = body.get("gender", None)
    specie = body.get("specie", None)
    dimension = body.get("dimension", None)

    if name is None or gender is None or specie is None or dimension is None:
        return jsonify({"error": "missing fields"}), 400

    character = Character(name=name, gender=Gender(gender), specie=Specie(specie), dimension=dimension)

    try:
        db.session.add(character)
        db.session.commit()
        db.session.refresh(character)

        return jsonify({"message": f"Character created {character.name}!"}), 201

    except Exception as error:
        return jsonify({"error": f"{error}"}), 500


@app.route("/character/<int:id>", methods=["GET"])
def get_character_by_id(id):
    try:
        character = Character.query.get(id)
        if character is None:
            return jsonify({'error': "Character not found!"}), 404
        return jsonify({"character": character.serialize()}), 200

    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

@app.route("/character/<int:id>", methods=["DELETE"])
@jwt_required()
def character_delete(id):
    try:
        character = Character.query.get(id)
        if character is None:
            return jsonify({"error":"Character not found!"}), 404
        db.session.delete(character)
        db.session.commit()

        return jsonify({"message":"character deleted"}),200
    
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"{error}"}), 500
    

@app.route("/seasons", methods=['GET'])
def get_all_seasons():
    try:
        seasons = Season.query.all()
        serialized_seasons = [season.serialize() for season in seasons]
        return jsonify({"seasons": serialized_seasons}), 200
    except Exception as error:
        return jsonify({"error":f"{error}"}),500    
    
@app.route("/season", methods=["POST"])
@jwt_required()
def create_season():

    body = request.json

    number = body.get("number", None)
    release_date = body.get("release_date", None)
    end_date = body.get("end_date", None)

    if number is None or release_date is None:
        return jsonify({"error":"Missing values"}), 400
    
    season_exist = Season.query.filter_by(number=number).first()
    if season_exist is not None:
        return jsonify({"error":f"Season {number} already exists"}), 400
    
    season = Season(number=number, release_date=release_date, end_date=end_date)
    
    try:
        db.session.add(season)
        db.session.commit()
        db.session.refresh(season)

        return jsonify({"message": "Season created"}),201

    except Exception as error:
        return jsonify({"error":{error}}), 500
    
@app.route("/episodes", methods=['GET'])    
def get_all_episodes():
    try:
        episodes = Episode.query.all()
        return jsonify({"episodes": [episode.serialize() for episode in episodes]}), 200
    except Exception as error:
        return jsonify({"error", f"{error}"}), 500
    
@app.route("/episode/<int:season_id>", methods=["POST"])
def create_episode(season_id):

    body = request.json

    name = body.get("name", None)
    duration = body.get("duration", None)
    number = body.get("number", None)
    release_date = body.get("release_date", None)

    if name is None or duration is None or number is None or release_date is None:
        return jsonify({"error":"Missing values"}), 400
    
    season_exist = Season.query.get(season_id)
    if season_exist is None:
        return jsonify({"error":f"Season not found"}), 404
    
    episode = Episode(name=name, duration=duration, number=number, release_date=release_date, season_id=season_id)

    try:
        db.session.add(episode)
        db.session.commit()
        db.session.refresh(episode)

        return jsonify({"episode":episode.serialize()}), 201
    
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
