from flask import Flask
from captive.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from captive.app import routes, models
