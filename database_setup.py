########Configuration###########
import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()
########End Configration########

class Genre(Base):
    __tablename__ = 'genre'

    name = Column(String(80), nullable = False)
    
    id = Column(Integer, primary_key = True)

class Movie(Base):
    __tablename__ = 'movie'

    name = Column(String(100), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(500))
    year = Column(Integer)
    director = Column(String(80))
    language = Column(String(20))

    genre_id = Column(Integer, ForeignKey('genre.id'))

    genre = relationship(Genre)
    

########Resume Confiugration####
engine = create_engine('sqlite:///movies.db')

Base.metadata.create_all(engine)
########End Configuration#######