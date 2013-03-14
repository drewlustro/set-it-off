###
# Controller to connect to social networks. Requires specific fields in user
# object
#
import urllib
import requests
from flask import Blueprint, redirect, url_for, request, session, g, flash
from flask.ext.oauth import OAuth
from app.models import User
from app.lib import facebook as fb
from app import config

controller = Blueprint('connect', __name__, url_prefix='/connect')

###
# Facebook

@controller.route('/facebook/authorize')
def facebook_authorize():
    session['next'] = request.args.get('next')
    session['close_action'] = request.args.get('close_action')
    perms = set(['email', 'read_stream', 'user_photos', 'friends_photos'])
    if request.args.get('extend'):
        perms.add(request.args['extend'])
    display = request.args.get('display', 'popup')

    # set the correct permissions here
    url = fb.auth_url(config.FACEBOOK_CLIENT_ID,
                      url_for('.facebook_callback', _external=True),
                      perms=list(perms), display=display)
    return redirect(url)


@controller.route('/facebook/callback')
def facebook_callback():
    code = request.args.get('code')
    close_action = session.get('close_action')
    if not code:
        # TODO deal with this error
        return redirect(close_action or
                        url_for('default.close_redirect', next_url='/'))
    try:
        facebook_info = fb.get_user_data_from_code(
            code,
            url_for('.facebook_callback', _external=True),
            config.FACEBOOK_CLIENT_ID,
            config.FACEBOOK_CLIENT_SECRET)
    except fb.GraphAPIError:
        return redirect(url_for('.facebook_authorize'))
    # check to see if the user already exists
    user = User.query.filter_by(
        facebook_id=facebook_info['id'],
        deleted=False).first()
    next_url = (session.get('next') or
                url_for('default.select_facebook_friends', _external=True))
    session['next'] = None
    # we are conencting the account
    if not g.user:
        if not user:
            session['facebook_info'] = facebook_info
            return redirect(url_for('default.signup', network='facebook'))
        g.user = user
        session['user_id'] = user.id
    elif user and g.user != user:
        flash('Your facebook session has expired. ' +
              'Please log in again to continue')
        next = url_for('default.index')
        return redirect(url_for('default.logout', next=next))
    else:
        g.user.set_facebook_info(facebook_info)

    return redirect(close_action or
                    url_for('default.close_redirect', next_url=next_url))

###
# Twitter

# Use Twitter as example remote application
oauth = OAuth()
twitter = oauth.remote_app(
    'twitter',
    # unless absolute urls are used to make requests, this will be added
    # before all URLs.  This is also true for request_token_url and others.
    base_url='https://api.twitter.com/1/',
    # where flask should look for new request tokens
    request_token_url='https://api.twitter.com/oauth/request_token',
    # where flask should exchange the token with the remote application
    access_token_url='https://api.twitter.com/oauth/access_token',
    # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
    # they mostly work the same, but for sign on /authenticate is
    # expected because this will give the user a slightly different
    # user interface on the twitter side.
    authorize_url='https://api.twitter.com/oauth/authenticate',
    # the consumer keys from the twitter application registry.
    consumer_key=config.TWITTER_CONSUMER_KEY,
    consumer_secret=config.TWITTER_CONSUMER_SECRET
)


@twitter.tokengetter
def get_twitter_token():
    """This is used by the API to look for the auth token and secret
    it should use for API calls.  During the authorization handshake
    a temporary set of token and secret is used, but afterwards this
    function has to return the token and secret.  If you don't want
    to store this in the database, consider putting it into the
    session instead.
    """
    user = g.user
    if user is not None and user.has_valid_twitter_token:
        return user.twitter_oauth_token, user.twitter_oauth_secret


@controller.route('/twitter/authorize')
def twtter_authorize():
    next = request.args.get('next')
    if g.user and g.user.has_valid_twitter_token:
        return redirect(next or "/")

    return twitter.authorize(callback=url_for(
        'twitter.oauth_authorized', next=next))


@controller.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(twitter_info):
    """Called after authorization.  After this function finished handling,
    the OAuth information is removed from the session again.  When this
    happened, the tokengetter from above is used to retrieve the oauth
    token and secret.

    Because the remote application could have re-authorized the application
    it is necessary to update the values in the database.

    If the application redirected back after denying, the response passed
    to the function will be `None`.  Otherwise a dictionary with the values
    the application submitted.  Note that Twitter itself does not really
    redirect back unless the user clicks on the application name.
    """
    next_url = request.args.get('next')
    if twitter_info is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url or url_for('default.index'))

    # check to see if the user already exists
    twitter_id = twitter_info['user_id']
    user = User.query.filter_by(twitter_id=twitter_id).first()
    next_url = next_url or url_for(
        'default.select_twitter_friends', twitter_connected=True)

    # we are conencting the account
    if not g.user:
        if not user:
            session['twitter_info'] = twitter_info
            return redirect(url_for('default.signup', network='twitter'))
        g.user = user
        session['user_id'] = user.id
    elif user and g.user and user != g.user:
        flash("That twitter account is already associated with another user."
              "Sign out of Twitter and try again.")
        return redirect(next_url)
    else:
        g.user.set_twitter_info(twitter_info)
    return redirect(next_url)

###
# Instagram

_AUTH_URL = 'https://api.instagram.com/oauth/authorize/?'\
            'client_id=%s&{0}&response_type=code' % (
                config.INSTAGRAM_CLIENT_ID)
_ACCESS_TOKEN_URL = 'https://api.instagram.com/oauth/access_token'


def _get_auth_url():
    return _AUTH_URL.format(urllib.urlencode(
        {'redirect_uri': url_for('.instagram_callback', _external=True)}))


def _get_access_token(code):
    data = {'client_id': config.INSTAGRAM_CLIENT_ID,
            'client_secret': config.INSTAGRAM_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': url_for('.callback', _external=True),
            'code': code}
    resp = requests.post(_ACCESS_TOKEN_URL, data=data)
    if resp.status_code != 200:
        return False
    return resp.json()


@controller.route('/instagram_authorize')
def authorize():
    session['next'] = request.args.get('next')
    return redirect(_get_auth_url())


@controller.route('/instagram_callback')
def callback():
    code = request.args.get('code')
    if not code:
        # TODO deal with this error
        return redirect(next_url='/')

    instagram_info = _get_access_token(code)
    if not instagram_info:
        # TODO deal with error
        return redirect(next_url='/')

    # check to see if the user already exists
    user = User.query.filter_by(
        instagram_id=instagram_info['user']['id'],
        deleted=False).first()
    next_url = (session.get('next') or
                url_for('default.select_instagram_friends', _external=True))
    session['next'] = None

    # we are conencting the account
    if not g.user:
        if not user:
            session['twitter_info'] = None
            session['instagram_info'] = instagram_info
            return redirect(url_for('default.signup', network='instagram'))
        g.user = user
        session['user_id'] = user.id
    elif user and g.user != user:
        flash('Your instagram session has expired. ' +
              'Please log in again to continue')
        next = url_for('default.index')
        return redirect(url_for('default.logout', next=next))
    else:
        g.user.set_instagram_info(instagram_info)

    return redirect(next_url)
