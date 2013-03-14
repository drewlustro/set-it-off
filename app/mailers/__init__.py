from functools import wraps
from flask_mail import Mail, Message
from flask import has_request_context, url_for, render_template
from app import config
from app.lib.database import db
from app.models import AutologinURL


class BaseMailer:
    queue = 'main'

    @classmethod
    def enqueue(cls, msg):
        params = {'subject': msg.subject,
                'recipients': msg.recipients,
                'body': msg.body,
                'html': msg.html,
                'sender': msg.sender,
                'reply_to': msg.reply_to,
                'category': getattr(msg, 'category', ''),
                'email_log_id': getattr(msg, 'email_log_id', None),
                'extra_headers': msg.extra_headers
                }
        get_resq().enqueue(BaseMailer, params)

    @classmethod
    def deliver(cls, msg, force=False, dogfood=True, deferred=False):
        if not msg:
            return False

        # HACKY HACK HACK
        # this allows the stuff to work from command line, it is
        # kind of terrible though. Ideally we just use current_app
        from app import application
        mail = Mail(application)
        cls.set_defaults(msg)

        # check the user's email preferences
        #for recipient in msg.recipients:
            #user = User.find_by_email(recipient)
            #if user and not EmailPreference.is_on(user, msg.category):
                #msg.recipients.remove(recipient)

        if len(msg.recipients) == 0:
            print "No recipients"
            return False

        # create an email log
        #el = EmailLog.log(msg)

        #if config.FLASK_ENV != 'production':
            # only send mails in debug mode if we force it
            #if not force:
                #body = msg.html
                #pass
                #if msg.body:
                    #body = msg.body
                #    pass
                # don't log if we're in test
                #if config.FLASK_ENV != 'test':
                #    pass
                #return True
        #else:  # log to mixpanel
            #pass

        # send or defer
        #if deferred:
            #cls.enqueue(msg)
        #else:
        mail.send(msg)

        # log message as sent
        #el.sent = True
        #db.add(el)
        #db.commit()

        if ((config.FLASK_ENV == 'production') or force) and dogfood:
            cls.send_dogfood(msg, deferred)
        return True

    @classmethod
    def send_dogfood(cls, msg, deferred=False):
        msg.subject = "[%s] %s" % (msg.recipients[0], msg.subject)
        old_recipients = msg.recipients
        old_sender = msg.sender
        msg.recipients = ['dogfood@lookmark.com']
        msg.sender = 'mail@lookmark.net'
        if deferred:
            cls.enqueue(msg)
        else:
            from app import application
            from app.lib.internal_mailer import InternalMailer
            ctx = None
            if not has_request_context():
                environ_overrides = {'HTTP_HOST': config.MAIL_URL_ROOT}
                ctx = application.test_request_context(
                    environ_overrides=environ_overrides)
                ctx.push()
            mailer = InternalMailer.mailer(application)
            mailer.send(msg)
            if ctx:
                ctx.pop()
        msg.recipients = old_recipients
        msg.sender = old_sender

    @classmethod
    def set_defaults(cls, msg):
        if not msg.sender:
            msg.sender = '"FollowBot" <digest@followbot.me>'
        if config.FLASK_ENV != 'production':
            msg.subject = ("[%s] " % config.FLASK_ENV) + msg.subject

    @staticmethod
    def sends_email(f):
        """Decorator"""
        @wraps(f)
        def decorated(*args, **kwargs):
            ctx = None
            if not has_request_context():
                # HACKY HACK HACK
                # this allows the stuff to work from command line, it is
                # kind of terrible though. Ideally we just use current_app
                from app import application
                environ_overrides = {'HTTP_HOST': config.MAIL_URL_ROOT}
                ctx = application.test_request_context(
                        environ_overrides=environ_overrides)
                ctx.push()

            ret = f(*args, **kwargs)

            if ctx:
                ctx.pop()
            return ret
        return decorated

    @staticmethod
    def work(params):
        """Deferred message sending."""
        ctx = None
        if not has_request_context():
            environ_overrides = {'HTTP_HOST': config.MAIL_URL_ROOT}
            ctx = app.test_request_context(
                    environ_overrides=environ_overrides)
            ctx.push()

        category = params.get('category', None)
        email_log_id = params.get('email_log_id', None)

        if email_log_id:
            email_log = EmailLog.query.get(email_log_id)
            del(params['email_log_id'])

        if category:
            del(params['category'])

        msg = Message(**params)
        msg.category = category

        if (msg.recipients == ['dogfood@followbot.me'] or
            msg.recipients == ['ops@flatironcollective.com']):
            from lookmark import app
            from lookmark.lib.internal_mailer import InternalMailer
            mailer = InternalMailer.mailer(app)
            mailer.send(msg)
        else:
            mail = Mail(app)
            mail.send(msg)
            if email_log:
                email_log.sent = True
                db.add(email_log)
                db.commit()

        if ctx:
            ctx.pop()
        return msg

    @staticmethod
    def unsubscribe_url(user=None, email=None):
        if user:
            short_url = AutologinURL.generate(
                user, url_for("default.unsubscribe", _external=True))
            return url_for("autologin.autologin", token=short_url.token,
                           _external=True)
        elif email:
            return url_for("account.unsubscribe", email=email, _external=True)

    @classmethod
    def render_body(cls, *args, **kwargs):
        user = kwargs.get('user', kwargs.get('to_user'))
        email = kwargs.get('email')
        unsubscribe_url = cls.unsubscribe_url(user, email)
        print "unsubscribe url : %s" % unsubscribe_url
        kwargs['unsubscribe_url'] = unsubscribe_url
        return render_template(*args, **kwargs)
