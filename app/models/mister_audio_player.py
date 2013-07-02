from app.lib import util
from path import path
import os
import sys
import subprocess

class MisterAudioPlayer:

    pid = None
    albums_path = None
    albums = None
    song_count = None
    daemon_subprocess = None
    command = None

    def __init__(self):
        self.albums_path = path('/music/')
        self.albums = self.albums_path.dirs()

    def play(self, song_name, interrupt_playing_song=True):
        print "Play %r" % song_name
        song = self.find_song(song_name)
        if song is not None:
            print "Found song!"
            if interrupt_playing_song:
                SongPlayJob.kill_current_song()
            util.get_resq().enqueue(SongPlayJob, song)
            return True
        return False

    def stop(self):
        SongPlayJob.empty_playlist()
        SongPlayJob.kill_current_song()

    def play_album(self, album_name, interrupt_playing_song=True):
        for a in self.albums:
            if a.namebase == album_name:
                songlist = self.songlist(album_name)
                if interrupt_playing_song and len(songlist) > 0:
                    self.stop()
                for song in songlist:
                    print "Playlist +: %s" % song.namebase
                    util.get_resq().enqueue(SongPlayJob, song)
                print "Added %d songs to playlist" % len(songlist)
                return True
        return False

    def find_song(self, song_name):
        for a in self.albums:
            songlist = self.songlist(a.namebase)
            for s in songlist:
                if s.namebase == song_name:
                    return s
        return None

    def songlist(self, album_name):
        album = None
        for a in self.albums:
            if a.namebase == album_name:
                album = a
                break
        songs = []
        if album is not None:
            songs += album.files('*.flac')
            songs += album.files('*.mp3')
            songs.sort()

            return songs
        return None

    

class SongPlayJob(object):
    queue = 'songplay'

    @staticmethod
    def empty_playlist():
        util.get_resq().remove_queue('songplay')
        return True

    @staticmethod
    def kill_current_song():
        cmd = 'pkill -f flac123'
        subprocess.call(cmd, shell=True)
        cmd = 'pkill -f mpg123'
        subprocess.call(cmd, shell=True)
        return True

    @staticmethod
    def perform(songpath):
        print "Running Job for %r" % songpath
        songpath = path(songpath)
        if songpath.ext == '.flac':
            cmd = 'flac123 "%s"' % songpath
        elif songpath.ext == '.mp3':
            cmd = 'mpg123 "%s"' % songpath
        else:
            print "Unsupported audio filetype: %r" % songpath.ext
            return

        subprocess.call(cmd, shell=True)
        return True

