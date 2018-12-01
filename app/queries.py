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
