from werkzeug.contrib.fixers import ProxyFix
import os

if not os.environ.get('FLASK_ENV', None):
    os.environ['FLASK_ENV'] = 'production'

from generalmethod import app
app.wsgi_app = ProxyFix(app.wsgi_app)
