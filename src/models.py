from flask_sqlalchemy import SQLAlchemy
from enum import Enum as PyEnum

db = SQLAlchemy()

#Enums

class Gender(PyEnum):
    FEMALE = "Female"
    MALE = "Male"
    UNDEFINED = "Undefined"

class Specie(PyEnum):
    HUMAN = "Human"
    ALIEN = "Alien"

class LocationType(PyEnum):
    PLANET = "Planet"
    STATION = "Space station"
    UNKNOWN = "Unknown"

#Tables

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(180), nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # Password no debe ser serializado
        }
    
    def __repr__(self):
        return f"<User: {self.email}>"


# Relacion de muchos a muchos respecto a episodios y personajes
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    specie = db.Column(db.Enum(Specie), nullable=False)
    dimension = db.Column(db.String(20), nullable=False)
    episode = db.relationship("CharacterApperances", backref="character", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender.value,
            "specie": self.specie.value,
            "dimension": self.dimension,
            "episode": self.episode
            }

    def __repr__(self):
        return "<Character %r>" % self.name 

# Relacion de muchos a muchos respecto a episodios y personajes
# Relacion de muchos a muchos respecto a localizaciones
class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    characters = db.relationship("CharacterApperances", backref="episode", lazy=True)
    season_id = db.Column(db.Integer, db.ForeignKey("season.id"))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "number": self.number,
            "release_date": self.release_date,
            "characters": self.characters,
            "season": self.season_id,
            }

    def __repr__(self):
        return "<Episode %r>" % self.name 
    

# Relacion de muchos a muchos respecto a episodios
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    dimension = db.Column(db.String(20), nullable=False)
    location_type = db.Column(db.Enum(LocationType), nullable=False, default=LocationType.UNKNOWN)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "dimension": self.dimension,
            "location type": self.location_type,
            }

    def __repr__(self):
        return f"<Location {self.name}>"

# Relacion de uno a muchos respecto a episodios
class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    episode = db.relationship("Episode", backref="season", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "number": self.number,
            "release_date": self.release_date,
            "end_date": self.end_date,
            # "episodes": [episode.serialize() for episode in self.episode]
            }    

    def __repr__(self):
        return f"<Season {self.number}>"


#Tablas relacionales

class CharacterApperances(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    episode_id = db.Column(db.Integer, db.ForeignKey("episode.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    
    def serialize(self):
        return {
            "id": self.id,
            "episodes": self.episode_id,
            "characters": self.character_id,
            }

    def __repr__(self):
        return f'<CharacterApperances character: {self.character_id} episode: {self.episode_id}>'