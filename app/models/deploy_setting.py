from app.lib import JSONEncodedDict
from app.lib.database import Base, db
from app import config
from sqlalchemy import Column, Integer, String, DateTime, Text
import datetime
import json


class DeploySetting(Base):
    __tablename__ = 'deploy_settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    namespace = Column(String(255), default='global')
    simple_data = Column(Text)
    json_data = Column(JSONEncodedDict)

    @property
    def value(self):
        if self.json_data:
            #print "%s:%s has JSONDATA! (%r)" % (self.namespace, self.key, self.json_data)
            return self.json_data
        if self.simple_data:
            #print "%s:%s has simple data. (%r)" % (self.namespace, self.key, self.simple_data)
            return self.simple_data
        return None

    @value.setter
    def value(self, newval):
        simple = True
        d = None
        try:
            d = json.loads(newval, sort_keys=True)
            if isinstance(d, dict):
                newval = d
                simple = False
        except ValueError:
            pass
        except TypeError:
            pass

        # it's a simple value, not of dictionary type
        if simple and not isinstance(newval, JSONEncodedDict) and not isinstance(newval, dict):
            # use NULL/default if empty string
            if newval == '':
                newval = None
            self.json_data = None
            self.simple_data = newval
            return

        # remove empty keyname from dict, if it exists
        try:
            newval.pop('', None)
        except KeyError:
            pass

        self.json_data = newval
        self.simple_data = None


    @classmethod
    def all(cls):
        return cls.query.order_by(cls.namespace.asc()).order_by(
                                    cls.key.asc()).all()

    @classmethod
    def namespaces(cls):
        cvs = cls.all()
        namespaces = set()
        for cv in cvs:
            namespaces.add(cv.namespace)
        return list(namespaces)

    @classmethod
    def get_value(cls, namespace='global', key=None):
        ds = cls.find_by_namespace_key(namespace, key)
        if ds:
            return ds.value
        return None

    @classmethod
    def find_by_namespace(cls, namespace=None):
        if not namespace:
            return None
        return cls.query.filter_by(namespace=namespace).all()

    @classmethod
    def find_by_namespace_key(cls, namespace='global', key=None):
        if not key or not namespace:
            return None
        return cls.query.filter_by(namespace=namespace, key=key).first()

    @classmethod
    def find_or_create_by_namespace_key(cls, namespace='global', key=None, default=None):
        ds = cls.find_by_namespace_key(namespace, key)
        if not ds:
            ds = cls(namespace=namespace, key=key, value=default)
            ds.create()
            return ds
        return cls.query.filter_by(namespace=namespace, key=key).first()


    def can_save(self):
        existing = DeploySetting.find_by_namespace_key(self.namespace, self.key)
        if existing and self.id == existing.id:
            return True
        elif existing:
            return False
        return True

    def create(self):
        if not self.namespace:
            self.namespace = 'global'
        if not self.can_save():
            return False
        result = super(DeploySetting, self).create()
        db.commit()
        return result

    def save(self):
        if not self.namespace:
            self.namespace = 'global'
        if not self.can_save():
            return False
        self.updated_at = datetime.datetime.utcnow()
        result = super(DeploySetting, self).save()
        db.commit()
        return result
