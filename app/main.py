from flask import Flask, render_template, request
from sqlalchemy import create_engine
from flask_login import login_user, logout_user, current_user, login_required,\
    LoginManager
from forms import SearchForm

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
        print(titles)
        return render_template('search_results.html', titles=titles)
    return render_template("index.html", form=form)
