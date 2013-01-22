import os
from app.config.common import *
FLASK_ENV = os.environ.get("FLASK_ENV", "development")

if FLASK_ENV == 'development':
    from app.config.development import *
elif FLASK_ENV == 'production':
    from app.config.production import *
