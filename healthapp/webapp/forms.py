"""Module containing forms for website.

Classes:
    RegistrationForm -- User registration form.
    LoginForm -- User login form.
    PostForm -- User post form.
    BloodPressureForm -- Astronaut form for adding a blood pressure record.
    Weight -- Astronaut form for adding a weight record.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from healthapp.models import User


class RegistrationForm(FlaskForm):
    """User registration form."""

    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),
                                                                     EqualTo('password')])
    role = StringField("Role: 'Admin', 'Astronaut', or 'Medic'", validators=[DataRequired()])
    submit = SubmitField('Register User')

    def validate_email(self, email):
        """
        Checks if there is a user with the entered email already in the database.

        Args:
            email -- email entered into the form to be checked.
        """
        # searches for user in the database.
        user = User.query.filter_by(email=email.data).first()

        if user:
            # sends error message if user is found in the database.
            raise ValidationError('Email already in use')

    def validate_role(self, role):
        """
        Checks if entered role is valid.

        Args:
            role -- role entered into the form to be checked.
        """
        if role.data not in ['Admin', 'Astronaut', 'Medic']:
            # sends error message if entered role isn't valid.
            raise ValidationError("Role must be either 'Admin', 'Astronaut', or 'Medic'")


class LoginForm(FlaskForm):
    """User login form."""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    """User post form."""

    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=60)])
    recipient = StringField('Recipient', validators=[DataRequired(), Email()])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Post')

    def validate_recipient(self, recipient):
        """
        Checks if the entered recipient is in the database.

        Args:
            recipient -- recipient email to be checked.
        """
        # finds user with the entered email in the database.
        user = User.query.filter_by(email=recipient.data).first()

        if not user:
            # sends error message if user is not found.
            raise ValidationError('Recipient email not registered')


class BloodPressureForm(FlaskForm):
    """Astronaut form for adding a blood pressure record."""

    blood_pressure = StringField('Blood Pressure', validators=[DataRequired(),
                                                               Length(min=1, max=12)])
    submit = SubmitField('Submit')


class WeightForm(FlaskForm):
    """Astronaut form for adding a weight record."""

    weight = StringField('Weight', validators=[DataRequired(), Length(min=1, max=12)])
    submit = SubmitField('Submit')
