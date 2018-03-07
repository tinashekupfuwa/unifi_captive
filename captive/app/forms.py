# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from captive.app.models import User

class LoginForm(FlaskForm):
#    username = StringField('Username', validators=[DataRequired()])
    pin = IntegerField('PIN', validators=[DataRequired()])
    submit = SubmitField('Apply PIN')

    def validate_pin(self,pin):
    	if len(str(pin.data))  < 6:
    		raise ValidationError("incorrect PIN")


class RegistrationForm(FlaskForm):
    phone = IntegerField(validators=[DataRequired()])
    submit = SubmitField('Request a PIN')

    def validate_phone(self, phone):
        if str(phone.data)[0] != '9' or len(str(phone.data)) < 9 :
            raise ValidationError('incorrect phone number')

