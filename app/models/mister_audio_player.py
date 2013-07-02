from app.lib import util
from app.lib import Daemon
from path import path
import os
import sys
import subprocess

class MisterAudioPlayer(Daemon):

    pid = None
    albums_path = None
    albums = None
    song_count = None
    daemon_subprocess = None
    command = None

    def __init__(self):
        super(MisterAudioPlayer, self).__init__("/tmp/mister_audio_player.pid")
        self.albums_path = path('/music/')
        self.albums = self.albums_path.dirs()

    def run_batch(self):
        batch_cmd = "batch <<< '%s'" % self.command
        print "BATCH:"
        print batch_cmd
        print ""
        subprocess.call(batch_cmd, shell=True)
        return True

    def run(self):
        print "Running subprocess"
        if self.daemon_subprocess:
            print "Forking Daemon"
            self.daemon_subprocess()
        return 0

    def play(self, songname):
        print "Play %r" % songname
        song = self.find_song(songname)
        if song is not None:
            print "Found song!"
            cmd = '/usr/local/bin/flac123 "%s"' % song
            self.command = cmd
            def play_subprocess():
                
                print cmd
                subprocess.call(['/usr/local/bin/flac123', song])
                return 0
            #spawn_daemon(play_subprocess)
            self.daemon_subprocess = play_subprocess
            return True
        return False

    def find_song(self, songname):
        for a in self.albums:
            for s in a.files('*.flac'):
                if s.namebase == songname:
                    return s
        return None

    def songlist(self, album_name):
        album = None
        for a in self.albums:
            if a.namebase == album_name:
                album = a
                break
        if album is not None:
            songs = album.files('*.flac')
            print "Songs for %r" % album
            songs.sort()
            return songs
        return None


def spawn_daemon(func):
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    # try: 
    #     pid = os.fork() 
    #     if pid > 0:
    #         # parent process, return and keep running
    #         return
    # except OSError, e:
    #     print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
    #     sys.exit(1)

    os.setsid()

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

    # do stuff
    func()

    # all done
    os._exit(os.EX_OK)