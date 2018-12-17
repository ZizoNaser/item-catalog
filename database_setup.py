#!/usr/bin/python
# #######Configuration###########
import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()
# #######End Configration########


class User(Base):
    __tablename__ = "user"

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250))


class Genre(Base):
    __tablename__ = 'genre'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    image = Column(String(80))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object data in easily serializable format"""
        return {
            'name': self.name,
            'id': self.id,

        }


class Movie(Base):
    __tablename__ = 'movie'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(500))
    year = Column(Integer)
    director = Column(String(80))
    language = Column(String(20))
    image = Column(String(80))

    genre_id = Column(Integer, ForeignKey('genre.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    genre = relationship(Genre)
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object data in easily serializable format"""
        return {
            'name': self.name,
            'description': self.description,
            'year': self.year,
            'director': self.director,
            'language': self.language,
            'id': self.id,
        }


# #######Resume Confiugration####
engine = create_engine('sqlite:///movies.db')

Base.metadata.create_all(engine)
# #######End Configuration#######
