#!/usr/bin/env python

import fabric.tasks
from fabric.api import run, task
import fabric.state
from fabric.api import settings

WEBS = ['db.lookmark.com']

fabric.state.env.user = 'www'
fabric.state.env.key_filename = '~/.ssh/id_rsa'
fabric.state.env.shell = '/bin/bash -l -c'

PROJECT_NAME = 'base'
PROJECT_PATH = '/fcc/%s' % PROJECT_NAME
PYTHON_PATH = '/fcc/envs/%s/bin' % PROJECT_NAME

JOBS = []


def update_code():
    """Checkout latest version of code from Git repo."""
    run("cd %s && git pull origin master" % PROJECT_PATH)


def update_packages():
    """pip install packages from the current requirements.txt file."""
    run('cd %s && %s/pip install -q -r requirements.txt' %
            (PROJECT_PATH, PYTHON_PATH))


def migrate():
    ["/fcc/envs/stathub/bin/alembic", "upgrade", "head"],
    run("export PYTHONPATH=%s;"\
        "cd %s && %s/alembic upgrade head" % (
            PROJECT_PATH, PROJECT_PATH, PYTHON_PATH))


def restart_web():
    """Restart lookmark web servers"""
    run('sudo supervisorctl restart %s' % PROJECT_NAME)


def restart_worker():
    for job in JOBS:
        run('sudo supervisorctl restart ' + job)


def start_scheduler():
    print "Starting scheduler"
    run('sudo supervisorctl start %s_scheduler' % PROJECT_NAME)


def stop_scheduler():
    print "Starting scheduler"
    run('sudo supervisorctl stop %s_scheduler' % PROJECT_NAME)


@task
def deploy():
    #stop_scheduler()
    update_code()
    update_packages()
    migrate()
    #restart_worker()
    restart_web()
    #start_scheduler()


if __name__ == '__main__':
    fabric.tasks.execute(deploy, hosts=WEBS)
