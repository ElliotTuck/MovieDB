from flask import Flask
from sqlalchemy import create_engine
app = Flask(__name__)
engine = create_engine('postgresql://Elliot@localhost:5432/moviedb')

@app.route('/')
def main():
    connection = engine.connect()
    result = connection.execute('SELECT * FROM Movie')
    movie_names = ''
    for row in result:
        movie_names += row['name'] + '\n'
    return movie_names
