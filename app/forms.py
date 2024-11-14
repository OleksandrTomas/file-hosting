from flask_wtf          import FlaskForm, CSRFProtect
from wtforms            import StringField, PasswordField, MultipleFileField, BooleanField, FieldList, FormField
from wtforms.validators import InputRequired, Length, EqualTo

# login page form
class LoginForm(FlaskForm):
    username = StringField(u'Username', validators = [InputRequired(), Length(4,20)])
    password = PasswordField(u'Password', validators = [InputRequired(),Length(4,50)])

# register page form
class RegistrationForm(FlaskForm):
    username = StringField(u'Username', validators = [InputRequired(), Length(4,20)])
    password = PasswordField(u'Password', validators = [InputRequired(), Length(4,50)])
    confirm = PasswordField(u'Repeat Password', validators = [InputRequired(),
                                                              EqualTo('password', message='Passwords must match')])

# admin page form
class FileUploadForm(FlaskForm):
    file = MultipleFileField(validators = [InputRequired()])
    check_public = BooleanField(u'Upload Public')
