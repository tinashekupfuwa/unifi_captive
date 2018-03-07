from captive.app import app, db
from captive.app.models import User, Auth

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Auth': Auth}
