from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    people_fav = db.relationship("People_fav", back_populates="user")
    planet_fav = db.relationship("Planet_fav", back_populates="user")
    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # no se serializa contraseña
        }
    
class Planet(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False )
    diameter= db.Column(db.Float, unique=False, nullable=False)
    gravity = db.Column(db.Float, unique=False, nullable=False )
    terrain = db.Column(db.String(250), unique=False, nullable=False)
    planet_fav = db.relationship("Planet_fav", back_populates="planet")
          
    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "gravity": self.gravity,
            "terrain": self.terrain,
        }
    
class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False )
    mass = db.Column(db.Float, unique=False, nullable=False)
    hair_color = db.Column(db.String, unique=False, nullable=False)
    skin_color = db.Column(db.String, unique=False, nullable=False)
    people_fav = db.relationship('People_fav', back_populates='people')
    def __repr__(self):
        return '<People %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
        }

class People_fav(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"))
    user = db.relationship("User", back_populates="people_fav")
    people = db.relationship("People", back_populates="people_fav")
    def __repr__(self):
       return '<People_fav %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "people_id": self.people_id,
            "user_id": self.user_id,
        }
    

class Planet_fav(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"))
    user = db.relationship("User", back_populates="planet_fav")
    Planet = db.relationship("Planet", back_populates="planet_fav")
    def __repr__(self):
       return '<Planet_fav %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "people_id": self.people_id,
            "user_id": self.user_id,
        }














