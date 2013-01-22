from werkzeug.contrib.fixers import ProxyFix
import os
if not os.environ.get('FLASK_ENV', None):
    os.environ['FLASK_ENV'] = 'production'

from app import application

application.wsgi_app = ProxyFix(application.wsgi_app)
