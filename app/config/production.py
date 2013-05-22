PROJECT_NAME = 'baseapp'
DATABASE = '%s_prod' % PROJECT_NAME
DATABASE_URI = 'mysql://root@localhost/'\
               '%s?unix_socket=/var/run/mysqld/mysqld.sock' % DATABASE
