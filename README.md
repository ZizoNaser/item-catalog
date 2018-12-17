# Item Catalog

Item Catalog is a flask web applicaion that you can through it add a list of movies and deferent genres.

# Set-up
* Install Vagrant
* Clone the [fullstack-nanodegree-vm repository.](https://github.com/udacity/fullstack-nanodegree-vm)
* Copy this project into "catalog" folder

# Usage
* Change directory to the fullstack-nanodegree-vm folder
run `vagrant up`

* after it finishs
`vagrant ssh`

* change directory to shared folder
`cd /vagrant/catalog`

* set up the database
`python database_setup.py`

* finally run the app
`python FinalProject.py`

* You can access the app from any brower using
`http://localhost:5000/`

# APIs

* You can get a list of all movies genres requesting:

`/genres/JSON/`

* And you can get  genre's movies  requesting:

`/genre/{Genre ID}/movies/JSON/`

* Also you can get movie details requesting:

`/genre/{Genre ID}/movie/{Movie ID}/JSON/`