########Create Flask App########
from flask import Flask
from flask import render_template, url_for, request, redirect, flash, jsonify, session, make_response
app = Flask(__name__)

########Configure Database######
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Movie, User

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

########End Configuration#######
########Configure Oauth#########
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests
import random, string

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read()
)['web']['client_id']
########End Configuration#######
########Configure Upload folder#
import os
UPLOAD_FOLDER = os.path.basename('static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
########End Configuration#######

@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)\
    for x in xrange(32))
    session['state'] = state
    return render_template('login.html',STATE=session['state'])

@app.route('/gconnect/', methods=['POST'])
def gconnect():
    
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Faild to upgrade the authorization code.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s'%access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # print("RESULT:",result)

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),501)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['sub'] != gplus_id:
        response = make_response(json.dumps("Token's user id dosn't match given user id."),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['aud'] != CLIENT_ID:
        response = make_response(json.dumps("Token's user id dosn't match app;s id."),401)
        print ("Token's user id dosn't match app;s id.")
        response.headers['Content-Type'] = 'application/json'
        return response
    #Check if the user is logged in the system
    stored_credentials = session.get('credentials')
    stored_gplus_id =  session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("The user's logged in aleardy."),200)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Store the access Token 
    session['provider'] = 'google'
    session['credentials'] = credentials.access_token
    session['gplus_id'] = gplus_id
    #Get user Info
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    params = {'access_token':credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id']= user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print "done!"
    return output

@app.route('/fbconnect/', methods=['POST'])
def fbconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json','r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json','r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' %(app_id, app_secret ,access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    userinfo_url = "https://graph.facebook.com/v2.2/me"

    result= json.loads(result)
    token = result['access_token']
    # print(token)
    # print(access_token)
    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email,picture&redirect=0&height=200&width=200 '% token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    # print(data)

    session['provider'] = 'facebook'
    session['username'] = data['name']
    session['email'] = data['email']
    session['facebook_id'] = data['id']
    session['picture'] = data['picture']['data']['url']
    # app_token ='2147172725536545|zV-1R7itxdd_LxmYnM0vEmE5eYQ'
    # url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % app_token

    # h = httplib2.Http()
    # result = h.request(url, 'GET')[1]
    # data = json.loads(result)
    # print(data)
    # session['picture'] = data['data']['url']

    user_id = getUserID(session['email'])
    print(user_id)
    if not user_id:
        user_id = createUser(session)
    session['user_id']= user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print "done!"
    return output


@app.route('/gdisconnect/')
def gdisconnect():
    credentials = session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps("Current User not Connected."),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'%credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps("The user's disconnected."),200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps("Failed to revoke token for given user"),400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbdisconnect/')
def fbdisconnect():
    facebook_id = session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions'% facebook_id
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "You have been logged out"

@app.route('/disconnect/')
def disconnect():
    # print "HI"
    # print session['provider']
    if 'provider' in session:
        if session['provider'] == 'google':
            gdisconnect()
            del session['gplus_id']
            del session['credentials'] 
        if session['provider'] == 'facebook':
            fbdisconnect()
            del session['facebook_id']
        del session['user_id']
        del session['username']
        del session['email']
        del session['picture']
        del session['provider']
        flash("You've successfully logged out!!")
        return redirect(url_for('showGenres'))
    else:
        flash("You're not logged in!!")
        return redirect(url_for('showGenres'))

@app.route('/')
@app.route('/genres/')
def showGenres():
    """This Page will display all genres."""
    session_db = DBSession()
    genres = session_db.query(Genre).all()
    if 'username' not in session:
        # flash("Welcome to Movies.")
        return render_template('publicGenres.html',genres=genres)
    else:
        return render_template('showGenres.html',genres=genres)

@app.route('/genres/JSON/')
def genresJSON():
    session_db = DBSession()
    genres = session_db.query(Genre).all()
    return jsonify(Genres=[genre.serialize for genre in genres])    

@app.route('/genre/new/', methods=['GET','POST'])
def newGenre():
    """This Page Will Create new genre."""
    if 'username' not in session:
        flash("Please login first.")
        return redirect('/')
    session_db=DBSession()
    if request.method == 'POST':
        
        if len(request.files) != 0:
            new_Genre = Genre(name=request.form['name'],description=request.form['description'],user_id=session['user_id'],)
            session_db.add(new_Genre)
            session_db.commit()
            new_Genre.image="Genre%d"%new_Genre.id
            session_db.add(new_Genre)
            session_db.commit()
            file = request.files['image']
            f = os.path.join("static/uploads/","Genre%d"%new_Genre.id)
            file.save(f)
        else:
            new_Genre = Genre(name=request.form['name'],description=request.form['description'],user_id=session['user_id'],image="missing%d"%random.randint(1,7))   
            session_db.add(new_Genre)
            session_db.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('newGenre.html')

@app.route('/genre/<int:genre_id>/edit/',methods=['GET','POST'])
def editGenre(genre_id):
    """This Page will edite a genre."""
    if 'username' not in session:
        flash("Please login first.")
        return redirect('/')
    session_db = DBSession()
    edited_genre = session_db.query(Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(edited_genre.user_id)
    if creator.id != session['user_id']:
        flash("Only the creator of the genre can edite it.")
        return redirect(url_for('showGenres'))
    if request.method == 'POST':
        old_name = edited_genre.name
        edited_genre.name = request.form['name']
        edited_genre.description=request.form['description']
        if len(request.files) != 0:
            if edited_genre.image == "Genre%d"%edited_genre.id:
                os.remove("static/uploads/Genre%d"%genre_id)
            edited_genre.image = "Genre%d"%edited_genre.id
            file = request.files['image']
            f = os.path.join("static/uploads/","Genre%d"%edited_genre.id)
            file.save(f)
        session_db.add(edited_genre)
        session_db.commit()
        flash("Genre:\"%s\" Edited!"%old_name)
        return redirect(url_for('showGenres'))
    else:
        return render_template('editeGenre.html',genre=edited_genre)

@app.route('/genre/<int:genre_id>/delete/',methods=['GET','POST'])
def deleteGenre(genre_id):
    """This Page will delete a genre and delete its movies."""
    if 'username' not in session:
        flash("Please login first.")
        return redirect('/')
    session_db =DBSession()
    genre = session_db.query(Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(genre.user_id)
    if creator.id != session['user_id']:
        flash("Only the creator of the genre can delete it.")
        return redirect('/')
    if request.method == 'POST':
        name = genre.name
        movies = session_db.query(Movie).filter_by(genre_id=genre_id)
        for movie in movies:
            session_db.delete(movie)
            session_db.commit()
        session_db.delete(genre)
        session_db.commit()

        if genre.image == "Genre%d"%genre_id:
            os.remove("static/uploads/Genre%d"%genre_id)
        
        flash("Gnere:\"%s\" Deleted!"%name)
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
    if 'username'  in session:
        return render_template('genre.html',genre=genre, movies=movies)
    else:
        return render_template('publicGenre.html',genre=genre, movies=movies)
@app.route('/genre/<int:genre_id>/movies/JSON/')
def moviesJSON(genre_id):
    session_db  = DBSession()
    genre = session_db.query(Genre).filter_by(id = genre_id).one()
    movies = session_db.query(Movie).filter_by(genre_id = genre.id).all()
    return jsonify(movies=[movie.serialize for movie in movies])

@app.route('/genre/<int:genre_id>/new/', methods=['GET','POST'])
def newMovie(genre_id):
    """This page will add new movie to a genre."""
    if 'username' not in session:
        flash("Please Log in first.")
        return redirect('/')
    session_db  = DBSession()
    if request.method == 'POST':
        new_movie = Movie(
                        name = request.form['name'],
                        year = request.form['year'],
                        description = request.form['description'],
                        director=request.form['director'],
                        language =request.form['language'],
                        genre_id=genre_id,
                        user_id=session['user_id']
                        )
        session_db.add(new_movie)
        session_db.commit()
        if len(request.files) != 0:
            new_movie.image="Movie%d"%new_movie.id
            session_db.add(new_movie)
            session_db.commit()
            file = request.files['image']
            f = os.path.join("static/uploads/","Movie%d"%new_movie.id)
            file.save(f)    
        else:
            new_movie.image="missing%d"%random.randint(1,7)
            session_db.add(new_movie)
            session_db.commit()
        
        flash("Movie \"%s\" Added!"%new_movie.name)
        return redirect(url_for('showMovies',genre_id=genre_id))
    else:

        return  render_template('newMovie.html',genre_id=genre_id)

@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/')
def showMovie(genre_id, movie_id):
    """this page will display movie %s in the genre %s"""%(movie_id,genre_id)

    session_db  = DBSession()
    genre = session_db.query(Genre).filter_by(id = genre_id).one()
    movie = session_db.query(Movie).filter_by(id = movie_id).one()

    return render_template("movie.html",movie=movie, genre=genre)

@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/edit/',methods=['GET','POST'])
def editMovie(genre_id, movie_id):
    if 'username' not in session:
        flash("Please Login first.")
        return redirect('/')
    session_db = DBSession()
    edited_movie = session_db.query(Movie).filter_by(id= movie_id).one()
    creator = getUserInfo(edited_movie.user_id)
    if creator.id != session['user_id']:
        flash("Only the creator of the Movie can edite it.")
        return redirect(url_for('showMovies',genre_id=genre_id))
    if request.method == 'POST':
        old_name = edited_movie.name
        
        edited_movie.director = request.form['director']
        edited_movie.name = request.form['name']
        edited_movie.year = request.form['year']
        edited_movie.description = request.form['description']
        edited_movie.language = request.form['language']

        if len(request.files) != 0:
            if edited_movie.image == "Movie%d"%edited_movie.id:
                os.remove("static/uploads/Movie%d"%movie_id)
            edited_movie.image = "Movie%d"%edited_movie.id
            file = request.files['image']
            f = os.path.join("static/uploads/","Movie%d"%edited_movie.id)
            file.save(f)

        session_db.add(edited_movie)
        session_db.commit()

        flash("Movie:\"%s\" edited."%old_name)
        return redirect(url_for('showMovies',genre_id=genre_id))
    else:
        return render_template('editMovie.html',genre_id=genre_id, movie = edited_movie)


@app.route('/genre/<int:genre_id>/movie/<int:movie_id>/delete/',methods= ['GET', 'POST'])
def deleteMovie(genre_id, movie_id):
    if 'username' not in session:
        return redirect('/login')
    session_db  = DBSession()
    deleted_movie = session_db.query(Movie).filter_by(id= movie_id).one()
    creator = getUserInfo(deleted_movie.user_id)
    if creator.id != session['user_id']:
        flash("Only the creator of the Movie can delete it.")
        return redirect(url_for('showMovies',genre_id=genre_id))
    if request.method == 'POST':
        session_db.delete(deleted_movie)
        session_db.commit()
        if deleted_movie.image == "Movie%d"%deleted_movie.id:
            os.remove("static/uploads/Movie%d"%movie_id)
        return redirect(url_for('showMovies',genre_id=genre_id))
    else:
        return render_template('deleteMovie.html', movie =deleted_movie)

def getUserID(email):
    try:
        session_db = DBSession()
        print(email)
        user = session_db.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
        

def getUserInfo(user_id):
    session_db = DBSession()
    user = session_db.query(User).filter_by(id = user_id).one()
    return user

def createUser(session):
    session_db = DBSession()
    newUser = User(name=session['username'], email=session['email'],\
                    picture=session['picture'])
    session_db.add(newUser)
    session_db.commit()
    user = session_db.query(User).filter_by(email= session['email']).one()
    return user.id

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.secret_key = "G4-y1axq4QX9CywFhJk3Xt7z"
    app.debug = True
    app.run(host = '0.0.0.0', port= 5000)