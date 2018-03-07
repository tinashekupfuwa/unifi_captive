# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from captive.app.models import User

class LoginForm(FlaskForm):
#    username = StringField('Username', validators=[DataRequired()])
    pin = StringField('PIN', validators=[DataRequired()])
    submit = SubmitField('Apply PIN')

    def validate_pin(self,pin):
    	if len(pin.data) != 6 or not check_is_number(pin.data):
    		raise ValidationError("incorrect PIN")


class RegistrationForm(FlaskForm):
    phone = StringField(validators=[DataRequired()])
    submit = SubmitField('Request a PIN')

    def validate_phone(self, phone):
        if phone.data[0] != '9' or len(phone.data) != 10 or not check_is_number(phone.data):
            raise ValidationError('incorrect phone number')
         

def check_is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


