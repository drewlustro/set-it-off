INTERNAL_MAIL_SERVER = 'smtp.mailgun.org'
INTERNAL_MAIL_USERNAME = 'postmaster@stathub.mailgun.org'
INTERNAL_MAIL_PASSWORD = '8o57bheyjmz1'
INTERNAL_MAIL_PORT = 587


HIPCHAT_TOKEN = '5b1e0251ebb93e7bffb0e9800d89a4'
HIPCHAT_ROOMID = 71567
HIPCHAT_SENDER = 'Exception'

ERROR_MAIL_SENDER_EMAIL = 'server-error@stathub.mailgun.org'
ERROR_MAIL_RECIPIENT_EMAIL = 'ops@flatironcollective.com'

CACHE_ENABLED = False
CACHE_URL = '127.0.0.1:11211'
CACHE_LOCK_DIR = '/tmp/cache/lock'

MAIL_URL_ROOT = 'localhost'

DATABASE = 'lazyfollow'
DATABASE_URI = 'mysql://root@localhost/'\
               '%s?unix_socket=/var/run/mysqld/mysqld.sock' % DATABASE

##
# Social Network

FACEBOOK_CLIENT_ID = ''
FACEBOOK_CLIENT_SECRET = ''


TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

INSTAGRAM_CLIENT_ID = ''
INSTAGRAM_CLIENT_SECRET = ''
