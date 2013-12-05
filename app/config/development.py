PROJECT_NAME = 'setitoff'
DATABASE = '%s_dev' % PROJECT_NAME
DATABASE_URI = 'mysql://root@localhost/'\
               '%s?unix_socket=/var/run/mysqld/mysqld.sock' % DATABASE
SERVICE_CONFIG_DIR = '/sites/setitoff/etc'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

MUSIC_DIR = '/music'
