from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(
        String(25), unique=True, nullable=False)
    last_name: Mapped[str] = mapped_column(
        String(25), unique=True, nullable=False)
    subscription_date: Mapped[str] = mapped_column(
        String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    fav_planet: Mapped[list['Favorite_Planet']]=relationship(
        back_populates='favorite_planet_by', cascade='all, delete-orphan')
    fav_character: Mapped[list['Favorite_Character']] = relationship(
        back_populates='favorite_character_by', cascade='all, delete-orphan')
    
    def __str__(self):
        return f'User {self.user}'
    def serialize(self):
        return{
            'id': self.id,
            'user': self.user,
            'email': self.email,
            'subscription_date': self.subscription_date,
            'is_active': self.is_active
        }


class Planet(db.Model):
    __tablename__ = 'planet'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    weather: Mapped[str] = mapped_column(
        String(25), unique=True, nullable=False)
    native_characters: Mapped[list['Character']] = relationship(
        back_populates='native_of', cascade='all, delete-orphan')
    favorite: Mapped[list['Favorite_Planet']] = relationship(
        back_populates='planet_inf', cascade='all, delete-orphan')

    def __str__(self):
        return f'Planet {self.name}'
    
    def serialize(self):
        return{
            'id': self.id,
            'name': self.name,
            'weather': self.weather
        }


class Character(db.Model):
    __tablename__= 'character'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    species: Mapped[str] = mapped_column(
        String(25), nullable=False)
    planet_origin: Mapped[int] = mapped_column(ForeignKey('planet.id'))
    native_of: Mapped[Planet] = relationship(
        back_populates='native_characters')
    favorites: Mapped[list['Favorite_Character']] = relationship(
        back_populates='character_inf', cascade='all, delete-orphan')
    def __str__(self):
        return f'{self.name}'
    
    def serialize(self):
        return{
            'id':self.id,
            'name':self.name,
            'species':self.species
        }
    
class Favorite_Planet(db.Model):
    __tablename__ = 'favorite_planet'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]= mapped_column(ForeignKey('user.id'))
    planet_id: Mapped[int]=mapped_column(ForeignKey('planet.id'))
    favorite_planet_by: Mapped[User]=relationship(
        back_populates='fav_planet')
    planet_inf: Mapped[Planet]=relationship(
        back_populates='favorite')
    
    def __str__(self):
        return f'{self.favorite_planet_by} likes {self.planet_inf}'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.favorite_planet_by.user if self.favorite_planet_by else None,
            'planet_id': self.planet_id,
            'planet': self.planet_inf.name if self.planet_inf else None
        }

class Favorite_Character(db.Model):
    __tablename__ = 'favorite_character'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]= mapped_column(ForeignKey('user.id'))
    character_id: Mapped[int]=mapped_column(ForeignKey('character.id'))
    favorite_character_by: Mapped[User] = relationship(
        back_populates='fav_character')
    character_inf: Mapped[Character]=relationship(
        back_populates='favorites')
    
    def __str__(self):
        return f'{self.favorite_character_by} likes {self.character_inf}'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.favorite_character_by.user if self.favorite_character_by else None,
            'character_id': self.character_id,
            'character': self.character_inf.name if self.character_inf else None
        }