import os
from flask import Flask, g, session
from app.lib.database import db
from app.models import User
from app.lib import error, util

application = Flask(__name__)
application.secret_key = '4m1t4m1t4m1t4m1t4m1t4m1t4m1t4m1t4m1t4m1t'

# ----------------------------------------------------------------------------
# Error Logging
# ----------------------------------------------------------------------------
if os.environ.get('FLASK_ENV', None) == 'production':
    application.logger.addHandler(error.get_mail_handler())
    application.logger.addHandler(error.get_hipchat_handler())


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
