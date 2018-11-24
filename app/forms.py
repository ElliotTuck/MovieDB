from wtforms import Form, StringField, validators

class SearchForm(Form):
    searchbar = StringField('Search Movies', [validators.DataRequired()])
