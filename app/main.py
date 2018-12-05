import re
import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import create_engine
from flask_login import login_user, logout_user, current_user, login_required,\
    LoginManager
from forms import SearchForm, MovieEntryForm, PersonEntryForm, LoginForm, \
    RegisterAudienceMemberForm, RegisterReviewerForm, ReviewForm, RatingForm, Search, Relation
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
        username = current_user.get_id()
        has_access = False
        if (not check_in_reviewer(db, username) and
            not check_in_audience(db, username)):
            has_access = True
        if search_type=='movie':
            result_set = movies_like(db, search_string)
            movie_listing = []
            for row in result_set:
                movie_listing.append((row.id, row.name.strip()))
            return render_template('search_results.html',
                                   movie_listing=movie_listing,
                                   has_access=has_access)
        else:
            result = person_like(db,search_string,search_type)
            person_listing = []
            for row in result:
                person_listing.append((row.id, row.name.strip()))
            return render_template('search_person.html',
                                    person_listing=person_listing,
                                   has_access=has_access)

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
    username = current_user.get_id().strip()
    form = MovieEntryForm(request.form)
    if request.method == 'POST' and form.validate():
        # insert movie info into Movie table
        insert_movie(db, form.name.data, form.release_date.data,
                     form.duration.data, form.description.data,
                     form.budget.data, form.mpaa_rating.data,
                     form.genres.data)
        flash('Movie information successfully entered.')
        return redirect(url_for('index'))
    return render_template('enter_movie.html', form=form)

@app.route('/enter_person', methods=['GET', 'POST'])
@login_required
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
        description = form.description.data
        insert_person(db, name, date_of_birth, nationalities, awards, jobs, description)
        flash('Person information successfully entered.')
        return redirect(url_for('index'))
    return render_template('enter_person.html', form=form)

@app.route('/enter_acting1', methods=['GET', 'POST'])
@login_required
def enter_acting1():
    form = Search(request.form)
    if request.method == 'POST' and form.validate():
        search_string = form.searchbar.data
        result_set = movies_like(db, search_string)
        movie_listing = []
        for row in result_set:
            movie_listing.append((row.id, row.name.strip()))
        return render_template('movie_results.html',
                                   movie_listing=movie_listing)
    return render_template("enter_acting.html", form=form)

@app.route('/movie_detail/<movie_id>')
@login_required
def select_movie(movie_id):
    movie_info = get_movie_info(db, movie_id)
    movie_genres = get_movie_genres(db, movie_id)
    genres = []
    for row in movie_genres:
        genres.append(row.genre.strip())
    genres_str = ", ".join(genres)
    return render_template('movie_detail.html', movie_id= movie_id, movie_info=movie_info,
                           genres_str=genres_str)


@app.route('/enter_acting2/<movie_id>', methods=['GET','POST'])
@login_required
def enter_acting2(movie_id):
    form = Search(request.form)
    if request.method == 'POST' and form.validate():
        search_string = form.searchbar.data
        ##################
        search_type = 'actor'
        result = person_like(db,search_string,search_type)
        person_listing = []
        for row in result:
            person_listing.append((row.id, row.name.strip()))
        return render_template('person_results.html', movie_id = movie_id, person_listing = person_listing)
    return render_template("enter_acting.html", form=form)

@app.route('/person_detail/<movie_id>/<person_id>')
@login_required
def select_person(movie_id, person_id):
    person_info = get_person_info(db, person_id)
    person_nationality = get_person_nation(db, person_id)
    nationalities = []
    for row in person_nationality:
        nationalities.append(row.nationality.strip())
    nationalities_str = ", ".join(nationalities)
    person_award = get_person_awards(db, person_id)
    awards = []
    for row in person_award:
        awards.append(row.award.strip())
        awards_str = ", ".join(awards)
    return render_template('person_detail.html', movie_id=movie_id, person_id=person_id, person_info=person_info,
     nationalities_str=nationalities_str, awards_str=awards_str)

@app.route('/add_relation/<movie_id>/<person_id>', methods=['GET','POST'])
@login_required
def add_relation(movie_id, person_id):
    form = Relation(request.form)
    if request.method == 'POST' and form.validate():
        relation = form.relation.data
        insert_relation(db, relation, movie_id, person_id)
        flash("Add relation successfully!")
    return render_template("add_relation.html", form=form)



@app.route('/movie/<id_val>')
def show_movie_info(id_val):
    movie_info = get_movie_info(db, id_val)
    movie_genres = get_movie_genres(db, id_val)
    genres = []
    for row in movie_genres:
        genres.append(row.genre.strip())
    genres_str = ", ".join(genres)
    reviews = get_movie_reviews(db, id_val)
    grade_values_inv = {v: k for k, v in grade_values.items()}
    avg_rating = get_avg_reviewer_rating_as_num(db, id_val)
    avg_rating = grade_values_inv[avg_rating] if avg_rating != -1 else 'No Reviewer Ratings'
    actors = get_actors(db, id_val)
    # note: this is not actually guaranteed to return the number of rows in a
    # select statement! (i.e. this is dangerous to do!)
    actor_count = actors.rowcount
    has_actors = actor_count > 0
    return render_template('movie_info.html', movie_info=movie_info,
                           genres_str=genres_str, reviews=reviews,
                           avg_reviewer_rating=avg_rating, actors=actors,
                           has_actors=has_actors)

@app.route('/person/<id_val>')
def show_person_info(id_val):
    person_info = get_person_info(db, id_val)
    person_nationality = get_person_nation(db, id_val)
    nationalities = []
    for row in person_nationality:
        nationalities.append(row.nationality.strip())
    nationalities_str = ", ".join(nationalities)
    person_award = get_person_awards(db, id_val)
    awards = []
    for row in person_award:
        awards.append(row.award.strip())
        awards_str = ", ".join(awards)
    return render_template('person_info.html', person_info=person_info,
                            nationalities_str=nationalities_str, awards_str=awards_str)

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

@app.route('/movie/<id_val>/rate', methods=['GET', 'POST'])
@login_required
def rate(id_val):
    form = RatingForm(request.form)
    if request.method == 'POST' and form.validate():
        movieId = id_val
        audienceId = current_user.get_id()
        rating = form.rating.data
        add_rating(db, movieId, audienceId, rating)
        flash('Rating successfully entered.')
        return redirect(url_for('show_movie_info',id_val= id_val))
    return render_template('Rating_page.html', form=form)

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
    account_info = get_reviewer_info(db, id_val)
    reviews = get_reviewer_reviews(db, id_val).fetchall()
    return render_template('reviewer_account_info.html',
                           account_info=account_info, reviews=reviews)

@app.route('/audience_member/<id_val>')
@login_required
def show_audience_member_account(id_val):
    account_info = get_audience_member_info(db, id_val)
    return render_template('audience_member_account_info.html',
                           account_info=account_info)

@app.route('/delete_review/<movie_id>/<reviewer_id>/<review_time>/<from_str>')
@login_required
def delete_review(movie_id, reviewer_id, review_time, from_str):
    if current_user.get_id().strip() == reviewer_id:
        remove_review(db, movie_id, reviewer_id, review_time)
        flash('Review deleted successfully')
    if from_str == 'from_movie_info':
        return redirect(url_for('show_movie_info', id_val=movie_id))
    else:
        return redirect(url_for('show_reviewer_account', id_val=reviewer_id))

@app.route('/movie/<id_val>/identify')
@login_required
def identifyuser(id_val):
    if check_in_reviewer(db, current_user.get_id()):
        return redirect(url_for('review',id_val=id_val))
    elif  check_in_audience(db, current_user.get_id()):
        return redirect(url_for('rate',id_val=id_val))
    else:
        flash('You are the adminstrator. Cannot add a review/rate.')
        return redirect(url_for('show_movie_info',id_val=id_val))

@app.route('/account/<id_val>')
@login_required
def direct_to_account(id_val):
    if check_in_reviewer(db, id_val):
        return redirect(url_for('show_reviewer_account', id_val=id_val))
    elif check_in_audience(db, id_val):
        return redirect(url_for('show_audience_member_account', id_val=id_val))
    else:
        return render_template('no_account.html')

