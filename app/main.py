import re
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import create_engine
from flask_login import login_user, logout_user, current_user, login_required,\
    LoginManager
from forms import SearchForm, MovieEntryForm, PersonEntryForm
from queries import * 

app = Flask(__name__)
app.secret_key = 'cse305'
db = create_engine('postgresql://Elliot:password@moviedb.ch3vwlfnxu62.us-west-2.rds.amazonaws.com:5432/moviedb')
login = LoginManager(app)
login.login_view = 'login'

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def main():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        search_string = form.searchbar.data
        search_type = form.searchtype.data if form.searchtype.data != 'None' \
            else 'NULL'

        if search_type=='movie':
            result_set = movies_like(db, search_string)
            movie_listing = []
            for row in result_set:
                movie_listing.append((row.id, row.name.strip()))
            return render_template('search_results.html',
                                   movie_listing=movie_listing)
         elif search_type=='actor':
            query = "SELECT person.id, person.name From person, actor where actor.id in (SELECT id FROM Person WHERE LOWER(Name) LIKE '%%{}%%')".format(
                search_string.lower())
            result = connection.execute(query)
            print(result.fetchone())
            actor_listing = []
            for row in result:
                actor_listing.append((row.id, row.name.strip()))
            return render_template('search_person.html',
                                    person_listing = actor_listing)
        # elif search_type=='director':

        # elif search_type=='producer':

        # else:

    return render_template("index.html", form=form)

@app.route('/enter_movie', methods=['GET', 'POST'])
def enter_movie():
    form = MovieEntryForm(request.form)
    if request.method == 'POST' and form.validate():
        # insert movie info into Movie table
        insert_movie(db, form.name.data, form.release_date.data,
                     form.duration.data, form.description.data,
                     form.budget.data, form.mpaa_rating.data, form.genres.data)
        flash('Movie information successfully entered.')
        return redirect(url_for('main'))
    return render_template('enter_movie.html', form=form)

@app.route('/enter_person', methods=['GET', 'POST'])
def enter_person():
    form = PersonEntryForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        date_of_birth = form.date_of_birth.data if form.date_of_birth.data \
            else 'NULL'
        nationalityString = form.nationality.data
        nationalities = re.split(', |,',nationalityString)
        awardString= form.award.data
        awards = re.split(', |,',awardString)
        jobs = form.job.data
        connection = db.connect()
        # insert movie info into Movie table
        result = connection.execute("INSERT INTO Person(Id, dateofbirth, name)" \
                           "VALUES (DEFAULT, '{}', '{}')" \
                           "RETURNING Id".
                           format(date_of_birth, name))
        id_val = result.fetchone()[0]
        # insert nation into PersonNationality table
        for nationality in nationalities:
            connection.execute("INSERT INTO PersonNationality(Id, nationality)"\
                                "VALUES ({},'{}')".format(id_val, nationality))
        for award in awards:
            connection.execute("INSERT INTO PersonAward(Id, award)"\
                                "VALUES ({},'{}')".format(id_val, award))

        # insert into actor/director/producer table
        print(jobs);
        for job in jobs:
            if job == 'Actor':
                connection.execute("INSERT INTO actor(id) VALUES({})".format(id_val))
            if job == 'Director':
                connection.execute("INSERT INTO director(id) VALUES({})".format(id_val))
            if job == 'Producer':
                connection.execute("INSERT INTO producer(id) VALUES({})".format(id_val))
        flash('Person information successfully entered.')
        return redirect(url_for('main'))
    return render_template('enter_person.html', form=form)

@app.route('/movie/<id_val>')
def show_movie_info(id_val):
    connection = db.connect()
    result = connection.execute('SELECT * FROM Movie WHERE Id = {}'.format(
        id_val))
    movie_info = result.fetchone()
    return render_template('movie_info.html', movie_info=movie_info)

@app.route('/person/<id_val>')
def show_person_info(id_val):
    connection = engine.connect()
    result = connection.execute('SELECT * FROM Person WHERE Id = {}'.format(id_val))
    person_info = result.fetchone()
    return render_template('person_info', person_info=person_info)