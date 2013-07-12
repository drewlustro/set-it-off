import os
from flask import Flask, g, session
from app.lib.database import db
from app.models import User
from app.lib import error, util
from app import config as config_module



application = Flask(__name__)
application.secret_key = '4m1t4m1t4m1t4m1t4m1t4m1t4m1t4m1t4m1t4m1t'
application.config.from_object(config_module)

# ----------------------------------------------------------------------------
# Error Logging
# ----------------------------------------------------------------------------
if os.environ.get('FLASK_ENV', None) == 'production':
    import logging
    file_handler = logging.FileHandler('/sites/logs/setitoff-flask.log')
    file_handler.setLevel(logging.DEBUG)
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    application.logger.addHandler(file_handler)


    #application.logger.addHandler(error.get_mail_handler())
    #application.logger.addHandler(error.get_hipchat_handler())


# ----------------------------------------------------------------------------
# Jinja Filters
# ----------------------------------------------------------------------------
from app.lib import custom_jinja_filters
custom_jinja_filters.register_filters(application)

# ----------------------------------------------------------------------------
# Controller Registration
# ----------------------------------------------------------------------------
import app.controllers
for blueprint in app.controllers.BLUEPRINTS:
    application.register_blueprint(blueprint)


# ----------------------------------------------------------------------------
# Request handlers
# ----------------------------------------------------------------------------
@application.before_request
def setup_request():
    g.user = None


@application.before_request
def before_request():
    if not g.user:
        if 'user_id' in session:
            session.setdefault('reboot_required', set())
            g.user = User.query.get(session['user_id'])
            if not g.user or g.user.deleted:
                g.user = None
        session.permanent = True

    if g.user and not session.get('_csrf_token'):
        session['_csrf_token'] = util.random_string()


@application.teardown_request
def shutdown_session(exception=None):
    db.remove()
    db.close()
