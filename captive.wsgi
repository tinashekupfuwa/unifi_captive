#!/usr/bin/python
import sys
import logging

activate_this = '/home/nryzhkov/flask/captive_portal/venv/bin/activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/nryzhkov/python/flask/captive_portal")

from captive.app import app as application
application.secret_key = 'Add your secret key'

