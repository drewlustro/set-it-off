import functools
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import config

engine = create_engine(config.DATABASE_URI,
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

    def create(self):
        db.add(self)
        db.commit()
        return True

    def save(self):
        db.add(self)
        db.commit()
        return True

    def delete(self):
        db.delete(self)
        db.commit()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def last(cls):
        return cls.query.order_by(desc('id')).first()

    @classmethod
    def find_by_eid(cls, id):
        from app.lib import util
        return cls.find_by_id(util.decode(id))

    @property
    def eid(self):
        from app.lib import util
        return util.encode(self.id)


Base = declarative_base(cls=BaseExt)
Base.query = db.query_property()


def init_db():
    import app.models
    app.models
    Base.metadata.create_all(bind=engine)

#--------------------------------------------------------------------
# Cache Config
#--------------------------------------------------------------------
# cache.ScopedSessionNamespace.create_session_container("ext:local_session", db)
# cache.cache_manager.regions['local_session'] = {'type': 'ext:local_session'}
# cache.set_caches('local_session', 'short_term')




# class cached(object):
#     def _get_namespace(self):
#         return "%s_%s" % (self._prefix, self._func.__name__)

#     def _get_key(self, args):
#         import hashlib
#         h = hashlib.sha1()
#         h.update('|'.join(str(x) for x in args))
#         return h.hexdigest()

#     def __init__(self, prefix):
#         self._prefix = prefix

#     def __call__(self, func):
#         self._func = func
#         return self

#     def get(self, *args):
#         if len(args) > 1:
#             raise Exception('Does not support arguments')
#         if not isinstance(args[0], Base) or not hasattr(args[0], 'id'):
#             raise Exception('Must run on a saved Model')

#         def memoized():
#             return self._func(*args)
#         data = cache.get(self._get_namespace(),
#                          self._get_key([args[0].id]), memoized)
#         # do a db merge for model arrays
#         if isinstance(data, list) and data and isinstance(data[0], Base):
#             data = [db.merge(m, load=False) if isinstance(m, Base) else m
#                     for m in data]
#         return data

#     def invalidate(self, obj):
#         cache.remove(self._get_namespace(), self._get_key([obj.id]))

#     def __get__(self, obj, type=None):
#         fn = functools.partial(self.get, obj)
#         fn.invalidate = functools.partial(self.invalidate, obj)
#         return fn
