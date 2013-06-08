PROJECT_NAME = 'setitoff'
DATABASE = '%s_dev' % PROJECT_NAME
DATABASE_URI = 'mysql://root@localhost/'\
               '%s?unix_socket=/var/run/mysqld/mysqld.sock' % DATABASE
SERVICE_CONFIG_DIR = '/home/drew/setitoff-config'
