import email

from app.models import User
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Surname', validators=[DataRequired()])
    # The Email() validator from WTForms requires an external dependency to be installed. email-validator
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # When you add any methods that match the pattern validate_<field_name>, WTForms takes those as custom validators and invokes them in addition to the stock validators.
    def validate_username(self, username):
        user = User.query.filter(User.username.ilike(username.data)).first()
        if user is not None:
            raise ValidationError(
                'This username is already taken, please try another one.')
        if ' ' in username.data:
            raise ValidationError('Your username may not contain spaces.')

    def validate_email(self, email):
        user = User.query.filter(User.email.ilike(email.data)).first()
        if user is not None:
            raise ValidationError(
                'There is already an account associated with this email address.')

        if not email.data.endswith("@bath.ac.uk"):
            raise ValidationError(
                'You must use a University of Bath email address, ending in @bath.ac.uk')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
