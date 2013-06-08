from flask import Blueprint, render_template, g, session, flash,\
    redirect, url_for, request
from app.models import User, ShairportService, AudioService, DeploySetting
from app.forms import LoginForm, SignupForm
from app.lib import filters
from app import application
from path import path

controller = Blueprint("default", __name__, url_prefix="")


@controller.route("/")
def index():
    return render_template('default/index.html')


@controller.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    
    if request.method == 'POST':
        application.jinja_env.cache.clear()
        namespace = request.form.get('namespace', None)
        
        

        if namespace == ShairportService.namespace():
            ss = ShairportService()
            if ss.update_from_form(request.form):
                flash("ShairportService updated & restarted.")
                session['reboot_required'].add(ShairportService.namespace())
                ss.restart()
            
            return redirect(url_for('.dashboard'))

        elif namespace == AudioService.namespace():
            aservice = AudioService()
            print 'audio:edit'
            if aservice.update_from_form(request.form):
                flash("AudioDevice updated & saved.")
                session['reboot_required'].add(AudioService.namespace())

            return redirect(url_for('.dashboard'))

        else:

            flash("Error saving shairport data.")
            return redirect(url_for('.dashboard'))

    settings = {}
    settings['audio:device'] = DeploySetting.find_or_create_by_namespace_key('audio', 'device', 'usbaudio').value

    return render_template('default/dashboard.html', settings=settings)

@controller.route('/reboot', methods=['GET', 'POST'])
def reboot():
    if request.method == 'POST' and request.form.get('reboot', False):
        import subprocess
        print "reboot"
        session.pop('reboot_required')
        subprocess.call('reboot', shell=True)
    return render_template('default/reboot.html', hide_banners=True)




@controller.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(csrf_enabled=False)
    next = None
    if g.user:
        return redirect(url_for(".index"))

    if form.validate_on_submit():
        u = User.login(form.email.data, form.password.data)
        if u:
            g.user = u
            session['user_id'] = g.user.id
            flash("Welcome back")
            return redirect(url_for(".index"))
        else:
            next = request.form.get('next', None)
            flash("Invalid e-mail address or password please try again.")

    if not next:
        next = request.args.get('next', None)
    return render_template("default/login.html", form=form)


@controller.route("/signup", methods=['GET', 'POST'])
def signup():
    if g.user:
        return redirect(url_for(".index"))

    form = SignupForm(csrf_enabled=False)
    if form.validate_on_submit():
        u = User.create(passwd=form.password.data,
                        email=form.email.data)
        if u:
            g.user = u
            session['user_id'] = g.user.id
            return redirect(url_for(".index"))
        else:
            flash("An account already exists with that username.")

    return render_template("default/signup.html", form=form)


@controller.route("/logout")
def logout():
    session.pop("user_id", None)
    g.user = None
    return redirect(url_for(".index"))
