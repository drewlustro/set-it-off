from flask import Blueprint, render_template, g, session, flash,\
    redirect, url_for, request
from app import application
from app.models import MisterAudioPlayer
from app.lib import util

controller = Blueprint("music", __name__, url_prefix="/music")


@controller.route("/play/<string:song>", methods=['GET', 'POST'])
def play(song):
    player = MisterAudioPlayer()
    message = "Play song %r" % song
    print message
    if player.play(song):
        player.run_batch()
    return util.render_json(200, {'message': message})


# @controller.route("/pause", methods=['GET', 'POST'])
# def pause():
#     print "Pause song"
#     return render_template('music/index.html')


@controller.route("/stop", methods=['GET', 'POST'])
def stop():
    message = "Stop song"
    print message
    return util.render_json(200, {'message': message})


