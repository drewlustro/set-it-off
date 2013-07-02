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
    player.play(song)
        
    return util.render_json(200, {'song': song})

@controller.route("/play/album/<string:album>", methods=['GET', 'POST'])
def play_album(album):
    player = MisterAudioPlayer()
    message = "Play album %r" % album
    player.play_album(album)
    return util.render_json(200, {'album': album})


# @controller.route("/pause", methods=['GET', 'POST'])
# def pause():
#     print "Pause song"
#     return render_template('music/index.html')


@controller.route("/stop", methods=['GET', 'POST'])
def stop():
    message = "Stop all songs"
    player = MisterAudioPlayer()
    player.stop()
    return util.render_json(200, {})


