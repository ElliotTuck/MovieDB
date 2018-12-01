from wtforms import Form, StringField, IntegerField, TextAreaField,\
    RadioField, SelectMultipleField, PasswordField, validators
from wtforms.fields.html5 import DateField

class SearchForm(Form):
    searchbar = StringField('Search Key word:', [validators.DataRequired()])
    searchtype = RadioField('Type:', [validators.DataRequired()],
                             choices=[('movie','movie'), ('actor','actor'),
                                      ('director','director'), ('producer','producer')])

class MovieEntryForm(Form):
    name = StringField('Name', [validators.DataRequired()])
    release_date = DateField('Release Date', [validators.Optional()])
    duration = IntegerField('Duration (minutes)', [validators.Optional()])
    description = TextAreaField('Description (max 256 characters)',
                                [validators.Length(max=256),
                                 validators.Optional()])
    budget = IntegerField('Budget', [validators.Optional()])
    mpaa_rating = RadioField('MPAA Rating', [validators.Optional()],
                             choices=[('G','G'), ('PG','PG'),
                                      ('PG-13','PG-13'), ('R','R'),
                                      ('NC-17','NC-17')])
    genres = SelectMultipleField('Genre', [validators.Optional()],
                                 choices=[('Horror','Horror'),
                                          ('Comedy','Comedy'),
                                          ('Drama','Drama'),
                                          ('Action','Action'),
                                          ('Thriller','Thriller')])

class PersonEntryForm(Form):
    name = StringField('Name', [validators.DataRequired()])
    date_of_birth = DateField('Date of Birth', [validators.DataRequired()])
    nationality = StringField('Nationality',[validators.Optional()])
    award = StringField('Award',[validators.Optional()])
    job = SelectMultipleField('Known for', [validators.Optional()],
                                 choices=[('Actor','Actor'),
                                          ('Director','Director'),
                                          ('Producer','Producer')])

class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired(),
                                        validators.Length(min=1,max=100)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.Length(min=1,max=50)])

class RegisterUserForm(Form):
    username = StringField('Username', [validators.DataRequired(),
                                        validators.Length(min=1,max=100)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.Length(min=1,max=50)])
    password2 = PasswordField('Enter Password Again',
                              [validators.DataRequired(),
                               validators.Length(min=1,max=50),
                               validators.EqualTo('password',
                                                  message='Passwords must match')])

class RegisterAudienceMemberForm(RegisterUserForm):
    pass

class RegisterReviewerForm(RegisterUserForm):
    name = StringField('Full Name', [validators.DataRequired(),
                                     validators.Length(max=100)])
    location = StringField('Location', [validators.Length(max=200)])
    organization = StringField('Organization', [validators.Length(max=256)])
