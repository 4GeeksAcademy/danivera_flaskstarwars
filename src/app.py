
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planetas as Planets, Personajes


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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/user', methods=['POST'])
def create_user():
    request_data=request.get_json()
    new_user=User(
    email=request_data.get('email'),
    password=request_data.get('password'),
    is_active=request_data.get('is_active',True)
)
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()),201

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# Endpoints para Favorites
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = User.query.get(1)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    favorites = {
        "planets": [planet.serialize() for planet in user.favorite_planetas],
        "people": [person.serialize() for person in user.favorite_personajes]
    }
    return jsonify(favorites), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = User.query.get(1) 
    planet = Planets.query.get(planet_id)
    
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    if planet in user.favorite_planetas:
        return jsonify({"error": "Planet already in favorites"}), 400
    
    user.favorite_planetas.append(planet)
    db.session.commit()
    
    return jsonify({"message": "Planet added to favorites"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user = User.query.get(1)  
    person = Personajes.query.get(people_id)
    
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    
    if person in user.favorite_personajes:
        return jsonify({"error": "Person already in favorites"}), 400
    
    user.favorite_personajes.append(person)
    db.session.commit()
    
    return jsonify({"message": "Person added to favorites"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user = User.query.get(1)  
    planet = Planets.query.get(planet_id)
    
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    if planet not in user.favorite_planetas:
        return jsonify({"error": "Planet not in favorites"}), 400
    
    user.favorite_planetas.remove(planet)
    db.session.commit()
    
    return jsonify({"message": "Planet removed from favorites"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user = User.query.get(1) 
    person = Personajes.query.get(people_id)
    
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    
    if person not in user.favorite_personajes:
        return jsonify({"error": "Person not in favorites"}), 400
    
    user.favorite_personajes.remove(person)
    db.session.commit()
    
    return jsonify({"message": "Person removed from favorites"}), 200




if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
