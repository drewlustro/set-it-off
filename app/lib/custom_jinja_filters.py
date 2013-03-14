import json


def register_filters(app):
    app.jinja_env.filters['to_json'] = to_json


def to_json(value):
    return json.dumps(value)
