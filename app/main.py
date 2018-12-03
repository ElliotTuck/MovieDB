import re
import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import create_engine
from flask_login import login_user, logout_user, current_user, login_required,\
    LoginManager
from forms import SearchForm, MovieEntryForm, PersonEntryForm, LoginForm, \
    RegisterAudienceMemberForm, RegisterReviewerForm, ReviewForm
from queries import * 
from models import User

app = Flask(__name__)
app.secret_key = 'cse305'
db = create_engine('postgresql://Elliot:password@moviedb.ch3vwlfnxu62.us-west-2.rds.amazonaws.com:5432/moviedb')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
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
        else:
            result = person_like(db,search_string,search_type)
            actor_listing = []
            for row in result:
                actor_listing.append((row.id, row.name.strip()))
            return render_template('search_person.html',
                                    person_listing = actor_listing)

    username = ''
    logged_in = False
    if current_user.is_authenticated:
        logged_in = True
        username = current_user.get_id()
        flash('Hello, {}!'.format(username))
    return render_template("index.html", form=form, logged_in=logged_in)

@app.route('/enter_movie', methods=['GET', 'POST'])
@login_required
def enter_movie():
    form = MovieEntryForm(request.form)
    if request.method == 'POST' and form.validate():
        # insert movie info into Movie table
        insert_movie(db, form.name.data, form.release_date.data,
                     form.duration.data, form.description.data,
                     form.budget.data, form.mpaa_rating.data, form.genres.data)
        flash('Movie information successfully entered.')
        return redirect(url_for('index'))
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
        return redirect(url_for('index'))
    return render_template('enter_person.html', form=form)

@app.route('/movie/<id_val>')
def show_movie_info(id_val):
    movie_info = get_movie_info(db, id_val)
    movie_genres = get_movie_genres(db, id_val)
    genres = []
    for row in movie_genres:
        genres.append(row.genre.strip())
    genres_str = ", ".join(genres)
    reviews = get_movie_reviews(db, id_val)
    reviewer_ratings = get_reviewer_ratings(db, id_val)
    count = 0
    sum = 0
    grade_values_inv = {v: k for k, v in grade_values.items()}
    for reviewer_rating in reviewer_ratings:
        rating = reviewer_rating.rating.strip()
        count += 1
        sum += grade_values[rating]
    avg_rating = round(sum/count) if count > 0 else -1
    avg_rating = grade_values_inv[avg_rating] if avg_rating != -1 else 'No Reviewer Ratings'
    return render_template('movie_info.html', movie_info=movie_info,
                           genres_str=genres_str, reviews=reviews,
                           avg_reviewer_rating=avg_rating)

@app.route('/person/<id_val>')
def show_person_info(id_val):
    connection = engine.connect()
    result = connection.execute('SELECT * FROM Person WHERE Id = {}'.format(id_val))
    person_info = result.fetchone()
    return render_template('person_info', person_info=person_info)

@login_manager.user_loader
def load_user(id):
    registered_user = get_user(db, id)
    if registered_user != None:
        username = registered_user.username.strip()
        password = registered_user.password.strip()
        return User(username, password)
    return None

@app.route('/register_audience_member', methods=['GET', 'POST'])
def register_audience_member():
    form = RegisterAudienceMemberForm(request.form)
    if request.method == 'GET':
        return render_template('register_audience_member.html', form=form)
    if request.method == 'POST' and form.validate():
        registered_user = get_user(db, form.username.data)
        if registered_user is not None:
            flash('User with that username already exists')
            return redirect(url_for('register_audience_member'))
        add_audience_member(db, form.username.data, form.password.data)
        flash('User successfully registered')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('register_audience_member.html', form=form) 

@app.route('/register_reviewer', methods=['GET', 'POST'])
def register_reviewer():
    form = RegisterReviewerForm(request.form)
    if request.method == 'GET':
        return render_template('register_reviewer.html', form=form)
    if request.method == 'POST' and form.validate():
        registered_user = get_user(db, form.username.data)
        if registered_user is not None:
            flash('User with that username already exists')
            return redirect(url_for('register_reviewer'))
        add_reviewer(db, form.username.data, form.password.data,
                     form.name.data, form.location.data,
                     form.organization.data)
        flash('User successfully registered')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('register_reviewer.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template('login.html', form=form)
    if request.method == 'POST' and form.validate():
        registered_user = get_user(db, form.username.data)
        if (registered_user is None or
            form.password.data != registered_user.password.strip()):
            flash('Username or password is invalid', 'error')
            return redirect(url_for('login'))
        registered_user = User(registered_user.username,
                               registered_user.password)
        login_user(registered_user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.route('/movie/<id_val>/review', methods=['GET', 'POST'])
@login_required
def review(id_val):
    form = ReviewForm(request.form)
    if request.method == 'POST' and form.validate():
        movieId = id_val
        reviewerId = current_user.get_id()
        reviewTime = datetime.datetime.now()
        review = form.review.data
        rating = form.rating.data
        add_review(db, movieId, reviewerId, reviewTime, review, rating)
        flash('Review successfully entered.')
        return redirect(url_for('show_movie_info',id_val= id_val))
    return render_template('Review_page.html', form=form)

@app.route('/highest_rated_movie')
def highest_rated_movie():
    movie_id = get_highest_rated_movie(db)
    return redirect(url_for('show_movie_info', id_val=movie_id))

@app.route('/most_reviewed_movie')
def most_reviewed_movie():
    movie_id = get_most_reviewed_movie(db)
    return redirect(url_for('show_movie_info', id_val=movie_id))

@app.route('/reviewer/<id_val>')
@login_required
def show_reviewer_account(id_val):
    reviews = get_reviewer_reviews(db, id_val)
    return render_template('reviewer_account_info.html', reviews=reviews)

@app.route('/delete_review/<movie_id>/<reviewer_id>/<review_time>')
@login_required
def delete_review(movie_id, reviewer_id, review_time):
    if current_user.get_id().strip() == reviewer_id:
        remove_review(db, movie_id, reviewer_id, review_time)
    return redirect(request.args.get('next') or url_for('index'))
