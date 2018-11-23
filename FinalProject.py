###@TODO Add the Language attribute to the movie

########Create Flask App########
from flask import Flask
from flask import render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

########Configure Database######
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Movie

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

########End Configuration#######

@app.route('/')
@app.route('/genres/')
def showGenres():
    """This Page will display all genres."""
    session_db = DBSession()
    genres = session_db.query(Genre).all()
    return render_template('index.html',genres=genres)

@app.route('/genres/JSON/')
def genresJSON():
    session_db = DBSession()
    genres = session_db.query(Genre).all()
    return jsonify(Genres=[genre.serialize for genre in genres])    

@app.route('/genre/new/', methods=['GET','POST'])
def newGenre():
    """This Page Will Create new genre."""
    session_db=DBSession()
    if request.method == 'POST':
        new_Genre = Genre(name=request.form['name'])
        session_db.add(new_Genre)
        session_db.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('newGenre.html')

@app.route('/genre/<int:genre_id>/edit/',methods=['GET','POST'])
def editGenre(genre_id):
    """This Page will edite a genre."""
    session_db = DBSession()
    edited_genre = session_db.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        edited_genre.name = request.form['name']
        session_db.add(edited_genre)
        session_db.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('editeGenre.html',genre=edited_genre)

@app.route('/genre/<int:genre_id>/delete/',methods=['GET','POST'])
def deleteGenre(genre_id):
    """This Page will delete a genre and delete its movies."""
    session_db =DBSession()
    genre = session_db.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        movies = session_db.query(Movie).filter_by(genre_id=genre_id)
        for movie in movies:
            session_db.delete(movie)
            session_db.commit()
        session_db.delete(genre)
        session_db.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('deleteGenre.html',genre=genre)
    

@app.route('/genre/<int:genre_id>/')
@app.route('/genre/<int:genre_id>/movies/')
def showMovies(genre_id):
    """This page will display all movies inside a genre"""
    session_db  = DBSession()
    genre = session_db.query(Genre).filter_by(id = genre_id).one()
    movies = session_db.query(Movie).filter_by(genre_id = genre_id).all()
    return render_template('genre.html',genre=genre, movies=movies)

@app.route('/genre/<int:genre_id>/movies/JSON/')
def moviesJSON(genre_id):
    session_db  = DBSession()
    genre = session_db.query(Genre).filter_by(id = genre_id).one()
    movies = session_db.query(Movie).filter_by(genre_id = genre_id).all()
    return jsonify(movies=[movie.serialize for movie in movies])

@app.route('/genre/<int:genre_id>/new/', methods=['GET','POST'])
def newMovie(genre_id):
    """This page will add new movie to a genre."""
    session_db  = DBSession()
    if request.method == 'POST':
        new_movie = Movie(name = request.form['name'], year = request.form['year'],
                        description = request.form['description'] ,director=request.form['director'],genre_id=genre_id)
        session_db.add(new_movie)
        session_db.commit()
        return redirect(url_for('showMovies',genre_id=genre_id))
    else:

        return  render_template('newMovie.html',genre_id=genre_id)

@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/')
def showMovie(genre_id, movie_id):
    return "this page will display movie %s in the genre %s"%(movie_id,genre_id)

@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/edit/',methods=['GET','POST'])
def editMovie(genre_id, movie_id):
    session_db = DBSession()
    edited_movie = session_db.query(Movie).filter_by(id= movie_id).one()
    print(edited_movie.name)
    if request.method == 'POST':
        edited_movie.name = request.form['name']
        edited_movie.year = request.form['year']
        edited_movie.description = request.form['description']
        edited_movie.director = request.form['director']
        session_db.add(edited_movie)
        session_db.commit()
        return redirect(url_for('showMovies',genre_id=genre_id))
    else:
        return render_template('editMovie.html',genre_id=genre_id, movie = edited_movie)


@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/delete/',methods= ['GET', 'POST'])
def deleteMovie(genre_id, movie_id):
    session_db  = DBSession()
    deleted_movie = session_db.query(Movie).filter_by(id= movie_id).one()
    if request.method == 'POST':
        session_db.delete(deleted_movie)
        session_db.commit()
        return redirect(url_for('showMovies',genre_id=genre_id))
    else:
        return render_template('deleteMovie.html', movie =deleted_movie)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port= 5000)