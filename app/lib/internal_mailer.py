from app import config
from flask_mail import Mail


class InternalMailer:
    @staticmethod
    def mailer(app):
        internal_mail = Mail()
        internal_mail.init_app(app)
        internal_mail.server = config.INTERNAL_MAIL_SERVER
        internal_mail.username = config.INTERNAL_MAIL_USERNAME
        internal_mail.password = config.INTERNAL_MAIL_PASSWORD
        internal_mail.port = config.INTERNAL_MAIL_PORT
        return internal_mail
