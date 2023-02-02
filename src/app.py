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
from models import db, User, Favorites, Characters, Planets
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# A partir de aquí los endpoints

@app.route('/user', methods=['GET'])
def handle_hello():
    allusers = User.query.all()
    print(allusers)
    results = list(map(lambda item: item.serialize(), allusers))
    print(results)
    return jsonify(results), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_info_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    print(user.serialize())
    
    return jsonify(user.serialize()), 200

@app.route('/favorites', methods=['GET'])
def handle_favorites():
    allfavorites = Favorites.query.all()
    print(allfavorites)
    results = list(map(lambda item: item.serialize(), allfavorites))
    print(results)
    return jsonify(results), 200

@app.route('/characters', methods=['GET'])
def handle_characters():
    allcharacters = Characters.query.all()
    print(allcharacters)
    results = list(map(lambda item: item.serialize1(), allcharacters))
    print(results)
    return jsonify(results), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_info_characters(character_id):
    character = Characters.query.filter_by(id=character_id).first()
    print(character.serialize())
    
    return jsonify(character.serialize()), 200

@app.route('/planets', methods=['GET'])
def handle_planets():
    allplanets = Planets.query.all()
    print(allplanets)
    results = list(map(lambda item: item.serialize(), allplanets))
    print(results)
    return jsonify(results), 200

@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_info_planets(planets_id):
    planets = Planets.query.filter_by(id=planets_id).first()
    print(planets.serialize())
    
    return jsonify(planets.serialize()), 200

@app.route('/user/<int:fav_id>/favorites', methods=['GET'])
def handle_user_favorites(fav_id):
    allusersfavs = Favorites.query.filter_by(user_id=fav_id).all()
    print(allusersfavs)
    results = list(map(lambda item: item.serialize(), allusersfavs))
    print(results)
    return jsonify(results), 200

@app.route('/user', methods=['POST'])
def add_new_user():
    allusers = User.query.all()
    results = list(map(lambda item: item.serialize(),allusers))
    print(results)
    request_body = json.loads(request.data)
    results.append(request_body)
    return jsonify(results), 200

@app.route('/user/<int:user_id>/favorites/planets', methods=['POST'])
def add_new_fav_planet(user_id):

    request_body = request.json

    fav_planets = Favorites.query.filter_by(user_id=user_id,planets_id=request_body["planets_id"]).first()
    fav_planet = Favorites(user_id=user_id, planets_id=request_body["planets_id"])

    if fav_planets is None:
        db.session.add(fav_planet)
        db.session.commit()
        return jsonify(fav_planet.serialize()), 200

    return jsonify({"msg":"El usuario seleccionado ya tiene ese favorito"}),404

@app.route('/user/<int:user_id>/favorites/characters', methods=['POST'])
def add_new_fav_character(user_id):
    
    request_body = request.json

    fav_characters = Favorites.query.filter_by(user_id=user_id,characters_id=request_body["characters_id"]).first()
    fav_character = Favorites(user_id=user_id, characters_id=request_body["characters_id"])

    if fav_characters is None:
        db.session.add(fav_character)
        db.session.commit()
        return jsonify(fav_character.serialize()), 200

    return jsonify({"msg":"El usuario seleccionado ya tiene ese favorito"}),404

@app.route('/user/<int:user_id>/favorites/planets', methods=['DELETE'])
def delete_planet(user_id):

    request_body = request.json

    print(request_body)

    fav_planet = Favorites.query.filter_by(user_id=user_id,planets_id=request_body["planets_id"]).first()

    print(fav_planet)

    if fav_planet is None:
        return jsonify({"msg":"El usuario seleccionado no tiene ese favorito"}),404
    
    db.session.delete(fav_planet)
    db.session.commit()

    return jsonify("El favorito ha sido eliminado"), 200

@app.route('/user/<int:user_id>/favorites/characters', methods=['DELETE'])
def delete_character(user_id):
    
    request_body = request.json

    print(request_body)

    fav_character = Favorites.query.filter_by(user_id=user_id,characters_id=request_body["characters_id"]).first()

    print(fav_character)

    if fav_character is None:
        return jsonify({"msg":"El usuario seleccionado no tiene ese favorito"}),404
    
    db.session.delete(fav_character)
    db.session.commit()

    return jsonify("El favorito ha sido eliminado"), 200



# Hasta aquí los endpoints

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
