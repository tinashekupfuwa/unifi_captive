import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TWILIO_ACCOUNT_SID = 'ACaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa64'
    TWILIO_AUTH_TOKEN = 'faaaaaaaaaaaaaaaaaaaaaaaaaaaaaac'
    TWILIO_PHONE_NUMBER = '+12602222222'

    UNIFI_WLC_IP = '10.2.1.96'
    UNIFI_WLC_PORT = '8443'
    UNIFI_WLC_USER = 'admin_api'
    UNIFI_WLC_PASSW = 'API_Pa$$w0rd1'
    INIFI_WLC_VER = 'v5'
    UNIFI_WLC_SITE_ID = 'default'
    UNIFI_WLC_SSL_VERIFY = False

    TIME_QOUTE = '60'

    SMS_ENABLE = 1
    SMPP_SERVER = '212.92.99.4'
    SMPP_PORT = 4442
    SMPP_USER = 'vbrr1:d5:deb51'
    SMPP_PASSW = 'MFj7c19A'
    SMPP_SOURCE = 'VBRR_WIFI'
