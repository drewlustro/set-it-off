import json


def register_filters(app):
    app.jinja_env.filters['to_json'] = to_json
    app.jinja_env.filters['javascript_time'] = javascript_time
    app.jinja_env.filters['format_number'] = format_number
    app.jinja_env.filters['formsafe'] = formsafe
    app.jinja_env.filters['selected_on'] = selected_on
    app.jinja_env.filters['checked_on'] = checked_on
    app.jinja_env.filters['deploy_setting'] = deploy_setting


def to_json(value):
    return json.dumps(value)


def deploy_setting(key, namespace='global', default=''):
    from app.models import DeploySetting
    cv = DeploySetting.find_by_namespace_key(namespace, key)
    #print "Deploy Setting %s:%s" % (key, namespace)
    if cv:
        #print "Returning %r" % (cv.value, )
        if cv.value is None:
            return ''
        return cv.value
    return default


def formsafe(object_attribute, default=''):
    return default if not object_attribute else object_attribute


def selected_on(test, other):
    return ' selected="selected"' if test == other else ''


def checked_on(test, other=True):
    return ' checked="checked"' if test == other else ''


def format_number(number, number_format="{:,d}"):
    return number_format.format(number)


def javascript_time(dt):
    """dt can either be a date or datetime object
    returns milliseconds since the unix epoch assuming dt is in utc"""
    return int(time.mktime(dt.timetuple())) * 1000
