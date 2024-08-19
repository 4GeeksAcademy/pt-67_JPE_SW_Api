import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Planet_fav, People_fav

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos
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

# Manejar errores y serializarlos como objetos JSON
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generar sitemap con todos los endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# listar people
@app.route('/people', methods=['GET'])
def get_people():
    # Obtener todos los registros de la tabla People
    people = People.query.all()
    
    # Serializar los registros
    serialized_people = [person.serialize() for person in people]
    
    # Devolver la respuesta JSON
    return jsonify(serialized_people), 200

#listar people id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    # Obtener el registro del personaje con el id proporcionado
    person = People.query.get(people_id)
    
    # Verificar si el personaje existe
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    
    # Serializar el registro
    serialized_person = person.serialize()
    
    # Devolver la respuesta JSON
    return jsonify(serialized_person), 200

# traer lista de planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    # Obtener todos los registros de la tabla Planet
    planets = Planet.query.all()
    
    # Serializar los registros
    serialized_planets = [planet.serialize() for planet in planets]
    
    # Devolver la respuesta JSON
    return jsonify(serialized_planets), 200


#traer planet_id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    # Obtener el registro del planeta con el id proporcionado
    planet = Planet.query.get(planet_id)
    
    # Verificar si el planeta existe
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    # Serializar el registro
    serialized_planet = planet.serialize()
    
    # Devolver la respuesta JSON
    return jsonify(serialized_planet), 200

# traer usuarios
@app.route('/users', methods=['GET'])
def get_users():
    # Obtener todos los registros de la tabla User
    users = User.query.all()
    
    # Serializar los registros
    serialized_users = [user.serialize() for user in users]
    
    # Devolver la respuesta JSON
    return jsonify(serialized_users), 200

#traer favoritos del usuario actual
@app.route('/users/favorites', methods=['GET'])
def get_users_favorites():
    # Obtener todos los usuarios
    users = User.query.all()

    # Inicializar una lista para almacenar los favoritos de todos los usuarios
    all_users_favorites = []

    for user in users:
        # Obtener los favoritos de personajes y planetas para cada usuario
        user_favorites = {
            "user_id": user.id,
            "email": user.email,
            "people_favorites": [people.serialize() for people in People.query.join(People_fav).filter(People_fav.user_id == user.id).all()],
            "planet_favorites": [planet.serialize() for planet in Planet.query.join(Planet_fav).filter(Planet_fav.user_id == user.id).all()]
        }
        
        # Añadir los favoritos del usuario a la lista
        all_users_favorites.append(user_favorites)
    
    # Devolver la respuesta JSON
    return jsonify(all_users_favorites), 200

#añadir planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # Obtén el ID del usuario de la solicitud (aquí asumo que tienes un método para obtener el usuario actual)
    user_id = request.json.get('user_id')
    
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400

    # Encuentra al usuario
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Encuentra el planeta
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    # Verifica si el planeta ya está en los favoritos del usuario
    existing_favorite = Planet_fav.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify({"error": "Planet is already in favorites"}), 400

    # Crea un nuevo registro en Planet_fav
    new_favorite = Planet_fav(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Planet added to favorites"}), 201

#añadir people favorito
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    # Obtén el ID del usuario de la solicitud (aquí asumo que tienes un método para obtener el usuario actual)
    user_id = request.json.get('user_id')
    
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400

    # Encuentra al usuario
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Encuentra la persona
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404

    # Verifica si la persona ya está en los favoritos del usuario
    existing_favorite = People_fav.query.filter_by(user_id=user_id, people_id=people_id).first()
    if existing_favorite:
        return jsonify({"error": "Person is already in favorites"}), 400

    # Crea un nuevo registro en People_fav
    new_favorite = People_fav(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Person added to favorites"}), 201

#borrar planeta favorito
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    # Obtén el ID del usuario de la solicitud (aquí asumo que tienes un método para obtener el usuario actual)
    user_id = request.json.get('user_id')
    
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400

    # Encuentra al usuario
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Encuentra el planeta en los favoritos del usuario
    favorite = Planet_fav.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    # Elimina el registro de favoritos
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Planet removed from favorites"}), 200

#borrar people favorito
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    # Obtén el ID del usuario de la solicitud (aquí asumo que el ID del usuario es parte de la solicitud en JSON)
    user_id = request.json.get('user_id')
    
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400

    # Encuentra al usuario
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Encuentra la persona en los favoritos del usuario
    favorite = People_fav.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    # Elimina el registro de favoritos
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Person removed from favorites"}), 200








    
   





















# Ejecutar el servidor
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
 
 