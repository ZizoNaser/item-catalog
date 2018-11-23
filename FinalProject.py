from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/genres/')
def showGenres():
    return "This Page will display all genres."

@app.route('/genre/new/')
def newGenre():
    return "This Page Will Create new genre."

@app.route('/genre/<int:genre_id>/edit/')
def editGenre(genre_id):
    return "This Page will edite genre %s" % genre_id

@app.route('/genre/<int:genre_id>/delete/')
def deleteGenre(genre_id):
    return "This Page will delete genre %s" % genre_id

@app.route('/genre/<int:genre_id>/')
@app.route('/genre/<int:genre_id>/movies/')
def showMovies(genre_id):
    return "this page will display all movies in genre %s"%genre_id

@app.route('/genre/<int:genre_id>/new/')
def newMovie(genre_id):
    return "this page will add new movie to the genre %s"%genre_id

@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/')
def showMovie(genre_id, movie_id):
    return "this page will display movie %s in the genre %s"%(movie_id,genre_id)

@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/edit/')
def editMovie(genre_id, movie_id):
    return "this page will edit movie %s in genre %s" %(movie_id,genre_id)

@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/delete/')
def delteMovie(genre_id, movie_id):
    return "This Page will delete movie %s from genre%s"%(movie_id,genre_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port= 5000)