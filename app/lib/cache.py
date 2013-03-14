import collections
import pylibmc
from beaker import cache, container
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from app import config

cache_opts = {
    'cache.lock_dir': config.CACHE_LOCK_DIR,

    'cache.regions': 'short_term',

    'cache.short_term.type': 'ext:memcached',
    'cache.short_term.expire': 600,
    'cache.short_term.memcache_module': 'pylibmc',
    'cache.short_term.url': config.CACHE_URL,

    'cache.short_term.enabled': config.CACHE_ENABLED
}


class RawCache:
    def __init__(self, tag_prefix='raw'):
        self.tag_prefix = tag_prefix
        self.mc = pylibmc.Client([config.CACHE_URL])

    def _tag(self, k):
        return "::".join([self.tag_prefix, k])

    def set(self, k, v, secs=60):
        tag = self._tag(k)
        self.mc.set(tag, v, secs)

    def get(self, k):
        tag = self._tag(k)
        res = self.mc.get(tag)
        return res

    def delete(self, k):
        tag = self._tag(k)
        self.mc.delete(tag)


class DummyCache:
    def get(self, key, **kw):
        return kw['createfunc']()


# TODO, do better than this
class DummyCacheManager:
    """Pass through manager if the cache is not enabled"""
    def get_cache(self, name, **kwargs):
        return DummyCache()

    def get_cache_region(self, name, region, **kwargs):
        return self.get_cache(name)

    @property
    def regions(self):
        return {}


class ScopedSessionNamespace(container.MemoryNamespaceManager):
    """A beaker cache type that caches on the current session

    We do this instead of something global so it can span multiple requests
    TODO make sure this changes after a request
    """
    def __init__(self, namespace, scoped_session, **kwargs):
        container.NamespaceManager.__init__(self, namespace)
        self._scoped_session = scoped_session

    @classmethod
    def create_session_container(cls, beaker_name, scoped_session):
        def create_namespace(namespace, **kwargs):
            return cls(namespace, scoped_session, **kwargs)
        cache.clsmap[beaker_name] = create_namespace

    @property
    def dictionary(self):
        """Return the cache dictionary used by this MemoryNamespaceManager."""
        session = self._scoped_session()
        try:
            nscache = session._beaker_cache
        except AttributeError:
            session._beaker_cache = nscache = collections.defaultdict(dict)
        return nscache[self.namespace]


if config.CACHE_ENABLED:
    cache_manager = CacheManager(**parse_cache_config_options(cache_opts))
else:
    cache_manager = DummyCacheManager()


#--------------------------------------------------------------------
# Super Simple Caching
#--------------------------------------------------------------------
_CACHES = {}


def get(namespace, key, createfunc):
    if not config.CACHE_ENABLED:
        return createfunc()

    cache = cache_manager.get_cache_region(namespace, _CACHES['local'])

    def l2_createfunc():
        l2_cache = cache_manager.get_cache_region(namespace, _CACHES['remote'])
        return l2_cache.get(key=key, createfunc=createfunc)
    return cache.get(key=key, createfunc=l2_createfunc)


def remove(namespace, key):
    if not config.CACHE_ENABLED:
        return
    cache_manager.get_cache_region(namespace, _CACHES['local']).remove(key)
    cache_manager.get_cache_region(namespace, _CACHES['remote']).remove(key)


def flush_all():
    client = pylibmc.Client([config.CACHE_URL])
    client.flush_all()


def set_caches(local_cache_region, remote_cache_region):
    _CACHES['local'] = local_cache_region
    _CACHES['remote'] = remote_cache_region
