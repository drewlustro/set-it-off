"""Shared controller filters."""

from functools import wraps
from flask import g, redirect, request, url_for, flash, abort


def requires_auth(f):
    """Authentication decorator for controller methods."""
    @wraps(f)
    def decorated(*args, **kwds):
        if g.user is None:
            flash("Please login to continue")
            return redirect(url_for('default.login', next=request.path))
        return f(*args, **kwds)
    return decorated


def requires_admin(f):
    """Authentication decorator for controller methods."""
    @wraps(f)
    def decorated(*args, **kwds):
        if not g.user or not g.user.is_admin:
            abort(404)
        return f(*args, **kwds)
    return decorated
