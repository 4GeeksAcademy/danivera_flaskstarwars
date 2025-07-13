from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Table, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


usuario_personaje = Table(
    "usuario_personaje",
    db.Model.metadata,
    db.Column("user_id", db.Integer, ForeignKey("user.id"), primary_key=True),
    db.Column("personajes_id", db.Integer, ForeignKey("personajes.id"), primary_key=True)    
)

usuario_planetas = Table(
    "usuario_planetas",
    db.Model.metadata,
    db.Column("user_id", db.Integer, ForeignKey("user.id"), primary_key=True),
    db.Column("planetas_id", db.Integer, ForeignKey("planetas.id"), primary_key=True)            
)

class User(db.Model):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)  
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    

    favorite_personajes = relationship("Personajes", secondary=usuario_personaje, 
    backref="usuarios_favoritos", lazy='dynamic')
    favorite_planetas = relationship("Planetas", secondary=usuario_planetas, 
    backref="usuarios_favoritos", lazy='dynamic')

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "is_active": self.is_active,
            "favorites": {
                "planets": [planet.serialize() for planet in self.favorite_planetas],
                "characters": [personaje.serialize() for personaje in self.favorite_personajes]
            }
        }

class Planetas(db.Model):
    __tablename__ = 'planetas'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(25), nullable=False)
    clima: Mapped[str] = mapped_column(String(120), nullable=False) 
    dimension: Mapped[str] = mapped_column(String(120), nullable=False)
    

    residentes = relationship("Personajes", backref="planeta_natal")

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "clima": self.clima,
            "dimension": self.dimension,
            "residentes": [r.serialize() for r in self.residentes]
        }    

class Personajes(db.Model):
    __tablename__ = 'personajes'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(25), nullable=False)
    especie: Mapped[str] = mapped_column(String(120), nullable=False)  
    planeta_id: Mapped[int] = mapped_column(ForeignKey("planetas.id"))
    
    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "especie": self.especie,
            "planeta_id": self.planeta_id,
            "planeta_nombre": self.planeta_natal.nombre if self.planeta_natal else None
        }