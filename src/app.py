import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Planet_fav, Planet_fav

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

# Obtener lista de planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    return jsonify(results), 200

# Obtener un solo planeta por ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({"msg": "Planeta no encontrado"}), 404

# Obtener lista de personas
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    results = [person.serialize() for person in people]
    return jsonify(results), 200

# Obtener una sola persona por ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify(person.serialize()), 200
    else:
        return jsonify({"error": "Persona no encontrada"}), 404

# Añadir a favoritos (planeta o persona)
@app.route('/favorites', methods=['POST'])
def add_to_favorites():
    data = request.get_json()
    planet_id = data.get('planet_id')
    people_id = data.get('people_id')

    if planet_id:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Planeta no encontrado"}), 404

        existing_favorite = Favoritos.query.filter_by(name=planet.name).first()
        if existing_favorite:
            return jsonify({"message": "Planeta ya está en favoritos"}), 200

        new_favorite = Favoritos(name=planet.name)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"message": "Planeta añadido a favoritos"}), 201

    elif people_id:
        person = People.query.get(people_id)
        if person is None:
            return jsonify({"error": "Persona no encontrada"}), 404

        existing_favorite = Favoritos.query.filter_by(name=person.name).first()
        if existing_favorite:
            return jsonify({"message": "Persona ya está en favoritos"}), 200

        new_favorite = Favoritos(name=person.name)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"message": "Persona añadida a favoritos"}), 201

    return jsonify({"error": "Se requiere planet_id o people_id"}), 400

# Eliminar de favoritos (planeta o persona)
@app.route('/favorites', methods=['DELETE'])
def remove_from_favorites():
    data = request.get_json()
    planet_id = data.get('planet_id')
    people_id = data.get('people_id')

    if planet_id:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Planeta no encontrado"}), 404

        favorite = Favoritos.query.filter_by(name=planet.name).first()
        if favorite is None:
            return jsonify({"error": "Planeta no encontrado en favoritos"}), 404

        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Planeta eliminado de favoritos"}), 200

    elif people_id:
        person = People.query.get(people_id)
        if person is None:
            return jsonify({"error": "Persona no encontrada"}), 404

        favorite = Favoritos.query.filter_by(name=person.name).first()
        if favorite is None:
            return jsonify({"error": "Persona no encontrada en favoritos"}), 404

        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Persona eliminada de favoritos"}), 200

    return jsonify({"error": "Se requiere planet_id o people_id"}), 400

# Obtener lista de favoritos por nombre
@app.route('/favorites', methods=['GET'])
def get_favorites():
    name = request.args.get('name')

    if not name:
        return jsonify({"error": "Nombre no proporcionado"}), 400

    favorites = Favoritos.query.filter_by(name=name).all()
    results = [favorite.serialize() for favorite in favorites]
    return jsonify(results), 200

# Ejecutar el servidor
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
 
 