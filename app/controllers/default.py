from flask import Blueprint, render_template, g, session, flash,\
    redirect, url_for, request
from app.models import User, ShairportService, AudioService,\
                        SystemStatusService, DeploySetting,\
                        WifiService, MisterAudioPlayer
from app.forms import LoginForm, SignupForm
from app import application


controller = Blueprint("default", __name__, url_prefix="")

@controller.route('/', methods=['GET', 'POST'])
def player():
    player = MisterAudioPlayer()
    return render_template('default/player.html', player=player)


@controller.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('default/status.html')
    shairport_service = ShairportService()
    audio_service = AudioService()
    wifi_service = WifiService()

    if request.method == 'POST':
        application.jinja_env.cache.clear()
        namespace = request.form.get('namespace', None)

        if namespace == ShairportService.namespace():
            if shairport_service.update_from_form(request.form):
                flash("ShairportService updated & restarted.")
                session['reboot_required'].add(ShairportService.namespace())
                shairport_service.restart()
            
            return redirect(url_for('.dashboard'))

        else:

            flash("Error saving shairport data.")
            return redirect(url_for('.dashboard'))

    settings = {}
    settings['audio:device'] = DeploySetting.find_or_create_by_namespace_key('audio', 'device', 'usbaudio').value

    return render_template('default/dashboard.html', settings=settings,
                           shairport_service=shairport_service,
                           audio_service=audio_service,
                           system_status_service=system_status_service)

@controller.route('/status', methods=['GET', 'POST'])
def status():
    system_status_service = SystemStatusService()
    return render_template('default/status.html',
                           system_status_service=system_status_service)

@controller.route('/airplay', methods=['GET', 'POST'])
def airplay():
    shairport_service = ShairportService()
    if request.method == 'POST':
        application.jinja_env.cache.clear()
        if shairport_service.update_from_form(request.form):
            flash("AirPlay Service updated & restarted.")
            session['reboot_required'].add(ShairportService.namespace())
            shairport_service.restart()
            return redirect(url_for('.airplay'))
    return render_template('default/airplay.html')

@controller.route('/bluetooth', methods=['GET', 'POST'])
def bluetooth():
    return render_template('default/bluetooth.html')


@controller.route('/advanced', methods=['GET', 'POST'])
def advanced():
    return render_template('default/advanced.html')

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
    session.pop("reboot_required", None)
    g.user = None
    return redirect(url_for(".index"))
