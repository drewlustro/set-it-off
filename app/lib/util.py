from datetime import datetime
import base64
import json
import hmac
import hashlib
import time
import re
import unicodedata
import random
import math
#import redis
#import pyres
from app import config

def filter_empty(string, default=''):
    if is_empty(string) or string == 'None':
        return default
    return string

def is_empty(var):
    if var is None:
        return True
    if isinstance(var, str) and var == '':
        return True
    if isinstance(var, unicode) and var == u'':
        return True
    if isinstance(var, dict) and var == dict():
        return True
    if isinstance(var, list) and len(var) <= 0:
        return True
    if isinstance(var, tuple) and len(var) <= 0:
        return True
    return False
    
def render_json(code, response):
    envelope = {}
    envelope['status'] = {'code': code}
    envelope['response'] = response
    return json.dumps(envelope)


def json_dict_from_form(request, name):
    keys = request.form.getlist(name + '_keys')
    values = request.form.getlist(name + '_values')
    if keys and values and len(keys) > 0 and len(values) > 0:
        d = dict(zip(keys, values))
        try:
            d.pop('', None)
        except KeyError:
            pass
        return d
    return dict()

# def get_resq():
#     """Returns a ResQ object with the correct redis connection"""
#     return pyres.ResQ(redis.Redis(
#         host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB))


# def get_redis():
#     return redis.StrictRedis(
#         host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


# def get_strict_redis():
#     return redis.StrictRedis(
#         host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


# def cache_clear_forced():
#     from app import cache
#     val = cache.get('clear_cache')
#     if val and cache.cache and cache.cache.clear:
#         cache.cache.clear()
#         return True
#     return False


def pretty_date(time=False, utc=True, compact=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    if utc:
        now = datetime.utcnow()
    else:
        now = datetime.now()

    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            if compact:
                return "now"
            return "just now"
        if second_diff < 60:
            if compact:
                return str(second_diff) + "s ago"
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            if compact:
                return "1m ago"
            return "a minute ago"
        if second_diff < 3600:
            if compact:
                return str(second_diff / 60) + "m ago"
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            if compact:
                return "1h ago"
            return "an hour ago"
        if second_diff < 86400:
            if compact:
                return str(second_diff / 3600) + "h ago"
            return str(second_diff / 3600) + " hours ago"

    if day_diff == 1:
        if compact:
            return "1d ago"
        return "Yesterday"
    if day_diff < 14:
        if compact:
            return str(day_diff) + "d ago"
        return str(day_diff) + " days ago"
    if day_diff < 31:
        if compact:
            return str(day_diff / 7) + "w ago"
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        month_count = day_diff / 30
        month_or_months = " months" if month_count > 1 else " month"
        if compact:
            return str(day_diff / 30) + month_or_months + " ago"
        return str(day_diff / 30) + " months ago"
    if compact:
        return str(day_diff / 365) + "y ago"
    return str(day_diff / 365) + " years ago"


def smart_truncate(content, length=200, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length + 1].split(' ')[0:-1]) + suffix


# stolen from SO
def unicode_truncate(s, length=200, encoding='utf-8'):
    encoded = s.encode(encoding)[:length]
    return encoded.decode(encoding, 'ignore')


def smart_unicode_truncate(s, length=200, encoding='utf-8'):
    encoded = s.encode(encoding)
    truncated = smart_truncate(encoded, length)
    return truncated.decode(encoding, 'ignore')


# stolen from SO
def base64_url_decode(inp):
    inp = inp.replace('-', '+').replace('_', '/')
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "=" * padding_factor
    return base64.decodestring(inp)


def parse_signed_request(signed_request, secret):
    l = signed_request.split('.', 2)
    encoded_sig = l[0]
    payload = l[1]

    sig = base64_url_decode(encoded_sig)
    data = json.loads(base64_url_decode(payload))

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        print('Unknown algorithm')
        return None
    else:
        expected_sig = hmac.new(secret, msg=payload,
                digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
        return None
    else:
        print('valid signed request received..')
        return data

def slugify(string, force_lowercase=True):
    """Convers the string to a slug."""
    if not isinstance(string, unicode):
        string = unicode(string)
    slug = unicodedata.normalize('NFKD', string)
    if force_lowercase:
        slug = slug.encode('ascii', 'ignore').lower()
    else:
        slug = slug.encode('ascii', 'ignore')
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    return slug


def random_string(length=32):
    choices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K',\
            'P', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z', '2', '3',\
            '4', '5', '6', '7', '8', '9']
    code = ''.join(random.choice(choices) for x in range(length))
    return code

# Code for encoded IDs, so we don't pass raw integers around in URLs
encode_mapping = {'0': 'x',
                  '1': 'j',
                  '2': 'p',
                  '3': 'e',
                  '4': 'a',
                  '5': 'l',
                  '6': 'm',
                  '7': 'z',
                  '8': 'd',
                  '9': 'k'}

decode_mapping = {}
for key, val in encode_mapping.items():
    decode_mapping[val] = key


def encode(id):
    if not id:
        return None
    id_string = str(id)
    ret = ''
    for char in id_string:
        ret += encode_mapping[char]
    return ret


def decode(id):
    id_string = str(id)
    ret = ''
    for char in id_string:
        ret += decode_mapping[char]
    return int(ret)


def timestamp(dt):
    """Converts a datetime to an integer timestamp."""
    return time.mktime(dt.timetuple())


EMAIL_REGEX = re.compile("[^@]+@[^@]+\.[^@]+")


def is_email(email):
    """Runs a VERY simple regex on an email address."""
    return EMAIL_REGEX.match(email)
