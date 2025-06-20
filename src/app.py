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
from models import db, User
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
    return jsonify({'msg':'ok', 'results':users_serialized}), 200

@app.route('/user/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user=User.query.get(id)
    if user is None:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    return jsonify({'msg':'ok', 'result': user.serialize()}), 200

@app.route('/user', methods=['POST'])
def create_user():
    body= request.get_json(silent=True)
    if body is None:
        return jsonify({'msg':'Debes enviar información en el body'}), 400
    if 'user' not in body:
        return jsonify({'msg':'Debes crear un user'}), 400
    if body['user'].strip()=='':
         return jsonify({'msg': 'Debes enviar un user válido'}), 400
    if 'first_name' not in body:
        return jsonify({'msg':'Debes enviar un campo first_name'}), 400
    if body['first_name'].strip() == '':
        return jsonify({'msg': 'Debes enviar un nombre válido'}), 400
    if 'last_name' not in body:
        return jsonify({'msg':'Debes enviar un campo last_name'}), 400
    if body['last_name'].strip() == '':
        return jsonify({'msg': 'Debes enviar un apellido válido'}), 400
    if 'email' not in body:
        return jsonify({'msg':'Debes enviar un campo email'}), 400
    if body['email'].strip() == '':
        return jsonify({'msg': 'Debes enviar un email válido'}), 400
    if 'password' not in body:
        return jsonify({'msg':'Debes enviar un campo password'}), 400
    if body['password'].strip() == '':
        return jsonify({'msg': 'Debes enviar una contraseña válida'}), 400
    
    new_user=User()
    new_user.user=body['user']
    new_user.first_name=body['first_name']
    new_user.last_name=body['last_name']
    new_user.email=body['email']
    new_user.password=body['password']
    new_user.subscription_date=datetime.datetime.now().strftime('%Y-%m-%d')
    new_user.is_active=True
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg':'ok', 'result': new_user.serialize()}), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
