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
from models import db, User, Character, Planet, Favorite_Planet, Favorite_Character
import datetime
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_serialized = []
    for user in users:
        users_serialized.append(user.serialize())
    return jsonify({'msg': 'ok', 'results': users_serialized}), 200


@app.route('/user/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    return jsonify({'msg': 'ok', 'result': user.serialize()}), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    characters_serialized = []
    for character in characters:
        characters_serialized.append(character.serialize())
    return jsonify({'msg': 'ok', 'results': characters_serialized}), 200


@app.route('/character/<int:id>', methods=['GET'])
def get_character_by_id(id):
    character = Character.query.get(id)
    if character is None:
        return jsonify({'msg': 'Personaje no encontrado'}), 404
    return jsonify({'msg': 'ok', 'result': character.serialize()}), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_serialized = []
    for planet in planets:
        planets_serialized.append(planet.serialize())
    return jsonify({'msg': 'ok', 'results': planets_serialized}), 200


@app.route('/planet/<int:id>', methods=['GET'])
def get_planet_by_id(id):
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({'msg': 'Planeta no encontrado'}), 404
    return jsonify({'msg': 'ok', 'result': planet.serialize()}), 200


@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': f'el usuario con id {user_id} no existe'}), 404
    favorites_characters_serialized = []
    for fav in user.fav_character:
        favorites_characters_serialized.append(fav.character_inf.serialize())

    favorites_planets_serialized = []
    for fav in user.fav_planet:
        favorites_planets_serialized.append(fav.planet_inf.serialize())

    return jsonify({'msg': 'ok', 'favorite_characters': favorites_characters_serialized, 'favorite_planets': favorites_planets_serialized}), 200


@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'user' not in body:
        return jsonify({'msg': 'Debes crear un user'}), 400
    if body['user'].strip() == '':
        return jsonify({'msg': 'Debes enviar un user válido'}), 400
    if 'first_name' not in body:
        return jsonify({'msg': 'Debes enviar un campo first_name'}), 400
    if body['first_name'].strip() == '':
        return jsonify({'msg': 'Debes enviar un nombre válido'}), 400
    if 'last_name' not in body:
        return jsonify({'msg': 'Debes enviar un campo last_name'}), 400
    if body['last_name'].strip() == '':
        return jsonify({'msg': 'Debes enviar un apellido válido'}), 400
    if 'email' not in body:
        return jsonify({'msg': 'Debes enviar un campo email'}), 400
    if body['email'].strip() == '':
        return jsonify({'msg': 'Debes enviar un email válido'}), 400
    if 'password' not in body:
        return jsonify({'msg': 'Debes enviar un campo password'}), 400
    if body['password'].strip() == '':
        return jsonify({'msg': 'Debes enviar una contraseña válida'}), 400

    new_user = User()
    new_user.user = body['user']
    new_user.first_name = body['first_name']
    new_user.last_name = body['last_name']
    new_user.email = body['email']
    new_user.password = body['password']
    new_user.subscription_date = datetime.datetime.now().strftime('%Y-%m-%d')
    new_user.is_active = True
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'ok', 'result': new_user.serialize()}), 201


@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def new_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if user is None:
        return jsonify({'msg': f'el user {user_id} no existe'}), 404
    if planet is None:
        return jsonify({'msg': f'el planeta {planet_id} no existe'}), 404

    new_fav_planet = Favorite_Planet()
    new_fav_planet.planet_id = user.id
    new_fav_planet.user_id = planet.id
    db.session.add(new_fav_planet)
    db.session.commit()

    return jsonify({'msg': 'ok', 'new fav': new_fav_planet.serialize()}), 201


@app.route('/favorite/<int:user_id>/character/<int:character_id>', methods=['POST'])
def new_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    character = Character.query.get(character_id)
    if user is None:
        return jsonify({'msg': f'el user {user_id} no existe'}), 404
    if character is None:
        return jsonify({'msg': f'el personaje {character_id} no existe'}), 404

    new_fav_character = Favorite_Character()
    new_fav_character.character_id = user.id
    new_fav_character.user_id = character.id
    db.session.add(new_fav_character)
    db.session.commit()

    return jsonify({'msg': 'ok', 'new fav': new_fav_character.serialize()}), 201


@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    body = request.get_json(silent=True)
    user = User.query.get(id)
    if user is None:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    if body is None:
        return jsonify({'msg': 'No se ha hecho ningún cambio'}), 400

    if 'user' in body:
        user.user = body['user']
    if 'email' in body:
        user.email = body['email']
    if 'first_name' in body:
        user.first_name = body['first_name']
    db.session.commit()
    return jsonify({'msg': 'ok', 'result': user.serialize()}), 200


@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(user_id, planet_id):
    fav_planet = Favorite_Planet.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if fav_planet is None:
        return jsonify({'msg': 'El favorito no existe'}), 404

    db.session.delete(fav_planet)
    db.session.commit()
    return jsonify({'msg': 'Favorito eliminado correctamente'}), 200

@app.route('/favorite/<int:user_id>/character/<int:character_id>', methods=['DELETE'])
def delete_character(user_id, character_id):
    fav_character = Favorite_Character.query.filter_by(
        user_id=user_id, character_id=character_id).first()
    if fav_character is None:
        return jsonify({'msg': 'El favorito no existe'}), 404

    db.session.delete(fav_character)
    db.session.commit()
    return jsonify({'msg': 'Favorito eliminado correctamente'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
