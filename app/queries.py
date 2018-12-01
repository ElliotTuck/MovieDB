def movies_like(db, search_str):
    query = "SELECT * FROM Movie WHERE LOWER(Name) LIKE '%%{}%%'".format(
        search_str.lower())
    result_set = db.execute(query)
    return result_set

def insert_movie(db, name, release_date, duration, description, budget,
                 mpaa_rating, genres):
    release_date = "'" + str(release_date) + "'" if release_date else 'NULL'
    duration = duration if duration else 'NULL'
    description = "'" + description + "'" if description != '' else 'NULL'
    budget = budget if budget else 'NULL'
    mpaa_rating = "'" + mpaa_rating + "'" if mpaa_rating != 'None' else 'NULL'
    query = "INSERT INTO Movie(Id, Name, ReleaseDate, Duration, Description, "\
        "Budget, MPAARating) VALUES (DEFAULT, '{}', {}, {}, {}, {}, {})"  \
        "RETURNING Id".format(name, release_date, duration, description,
                              budget, mpaa_rating)
    result_set = db.execute(query)
    id_val = result_set.fetchone()[0]
    for genre in genres:
        query = "INSERT INTO MovieGenre(Id, Genre) VALUES ({}, '{}')".format(
            id_val, genre)
        db.execute(query)

def person_like(db, search_str, role):
    query = "SELECT person.id, person.name From person, {} where {}.id = person.id AND LOWER(person.Name) LIKE '%%{}%%'".format(role,role,
                search_str.lower())
    result_set = db.execute(query)
    return result_set

def get_user(db, username):
    query = "SELECT * FROM UserAccount WHERE Username = '{}'".format(username)
    result_set = db.execute(query)
    return result_set.first()

def add_user(db, username, password):
    query = "INSERT INTO UserAccount(Username, Password) VALUES ('{}', " \
        "'{}')".format(username, password)
    db.execute(query)

def add_audience_member(db, username, password):
    add_user(db, username, password)
    query = "INSERT INTO AudienceMember(Username, Since, Status) VALUES " \
        "('{}', DEFAULT, 'None')".format(username)
    db.execute(query)

def add_reviewer(db, username, password, name, location, organization):
    add_user(db, username, password)
    location = "'" + location + "'" if location != '' else 'NULL'
    organization = "'" + organization + "'" if organization != '' else 'NULL'
    query = "INSERT INTO Reviewer(Username, Name, Location, Organization, " \
        "CriticalScore) VALUES ('{}', '{}', {}, {}, 100)".format(
            username, name, location, organization)
    db.execute(query)

def get_movie_info(db, movie_id):
    query = "SELECT * FROM Movie WHERE Id = {}".format(movie_id)
    result_set = db.execute(query)
    return result_set.first()

def get_movie_genres(db, movie_id):
    query = "SELECT * FROM MovieGenre WHERE Id = {}".format(movie_id)
    result_set = db.execute(query)
    return result_set

def get_movie_reviews(db, movie_id):
    query = "SELECT * FROM Review INNER JOIN Reviewer ON Review.ReviewerId = "\
        "Reviewer.Username WHERE Review.MovieId = {}".format(movie_id)
    result_set = db.execute(query)
    return result_set

def add_review(db, movieid, reviewerid, reviewtime, review, rating):
    query = "INSERT INTO Review (movieid, reviewerid, reviewtime, review, rating) 
            VALUES({},'{}',{},'{}','{}')".format(movieid, reviewerid, reviewtime, review, rating)
    db.execute(query)
