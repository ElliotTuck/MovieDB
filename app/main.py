from flask import Flask, render_template, request
from sqlalchemy import create_engine
from flask_login import login_user, logout_user, current_user, login_required,\
    LoginManager
from forms import SearchForm, MovieEntryForm

app = Flask(__name__)
engine = create_engine('postgresql://Elliot@localhost:5432/moviedb')
login = LoginManager(app)
login.login_view = 'login'

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def main():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        search_string = form.searchbar.data
        connection = engine.connect()
        query = "SELECT * FROM Movie WHERE LOWER(Name) LIKE '%%{}%%'".format(
            search_string.lower())
        result = connection.execute(query)
        titles = []
        for row in result:
            titles.append(row['name'].strip())
        return render_template('search_results.html', titles=titles)
    return render_template("index.html", form=form)

@app.route('/enter_movie', methods=['GET', 'POST'])
def enter_movie():
    form = MovieEntryForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        release_date = form.release_date.data if form.release_date.data \
            else 'NULL'
        duration = form.duration.data if form.duration.data else 'NULL'
        description = form.description.data
        budget = form.budget.data if form.budget.data else 'NULL'
        mpaa_rating = form.mpaa_rating.data if form.mpaa_rating.data \
            else 'NULL'
        genres = form.genres.data
        connection = engine.connect()
        result = connection.execute('SELECT COUNT(*) FROM Movie')
        num_movies = result.fetchone()[0]
        id_val = int(num_movies) + 1
        connection.execute("INSERT INTO Movie(Id, Name, ReleaseDate,"   \
                           "Duration, Description, Budget, MPAARating)" \
                           "VALUES ({}, '{}', '{}', {}, '{}', {}, '{}')".format
                           (id_val, name, release_date, duration, description,
                            budget, mpaa_rating))
        return 'submitted successfully'
    return render_template('enter_movie.html', form=form)
