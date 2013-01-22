from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

_DATABASE_URL = 'mysql://root@localhost/'\
                'dailylog?unix_socket=/var/run/mysqld/mysqld.sock'
engine = create_engine(_DATABASE_URL,
                       convert_unicode=True,
                       echo=False,
                       pool_recycle=3600,
                       pool_size=20,
                       max_overflow=40)
db = scoped_session(sessionmaker(autocommit=False,
                                 autoflush=True,
                                 expire_on_commit=False,
                                 bind=engine))


class BaseExt(object):
    # default table args
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    # stolen from http://bit.ly/btqa1C comments
    def __repr__(self):
        return "%s(%s)" % ((self.__class__.__name__), ', '.join(["%s=%r" % \
        (key, getattr(self, key)) for key in sorted(self.__dict__.keys()) \
        if not key.startswith('_')]))

    # finally moved into the base
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


Base = declarative_base(cls=BaseExt)
Base.query = db.query_property()


def init_db():
    import app.models
    app.models
    Base.metadata.create_all(bind=engine)
