from app.lib import Service
from app.lib import util
import subprocess

class AudioService(Service):

    config_file = 'audio.config'
    default_contents = 'usbaudio'
    profiles = ['usbaudio', 'pulse', 'original']

    @classmethod
    def namespace(cls):
        return 'audio'

    @property
    def display_name(self):
        raise 'Linux Audio Subsystem'

    def restart_audio(self):
        output = ''
        try:
            cmd = 'sudo /etc/init.d/alsa-utils restart'
            output += subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            output += 'Error restarting alsa-utils!<br>'
            output += '%s <br>' % (e)

        try:
            cmd = 'sudo /etc/init.d/pulseaudio restart'
            output += subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            output += 'Error restarting pulseaudio!<br>'
            output += '%s <br>' % (e)

        try:
            cmd = 'sudo /etc/init.d/shairport restart'
            output += subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            output += 'Error restarting shairport (airplay)!<br>'
            output += '%s <br>' % (e)

        try: 
            cmd = 'sudo /etc/init.d/bluetooth-agent restart'
            output += subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            output += 'Error restarting bluetooth-agent!<br>'
            output += '%s <br>' % (e)
        return output

    def update_from_form(self, form):
        from app.models import DeploySetting
        ds = DeploySetting.find_or_create_by_namespace_key(AudioService.namespace(), 'device')
        device = util.filter_empty(form.get('device'), self.default_contents)
        if (device != self.get()):
            print "Saved new audio device. <old: %s, new: %s>" % (self.get(), device)
            ds.value = device
            ds.save()
            self.set(value=ds.value)
            self.save()
            return True
        return False

    @property
    def device_display_name(self):
        device = self.get()
        if device == 'usbaudio':
            return 'Hi-Fi USB Audio'
        elif device == 'pulse':
            return '3.5mm Audio Jack (RasPi PWM)'
        else:
            return 'RasPi Factory Default'

    def copy_config_file_commands(self):
        device = self.get()
        if not device:
            device = 'usbaudio'
        cmd_alsa_base = 'cp /sites/set-it-off/profiles/alsa/alsa-base.conf.%s /etc/modprobe.d/alsa-base.conf' % device
        cmd_asound = 'cp /sites/set-it-off/profiles/asound/asound.conf.%s /etc/asound.conf' % device

        commands = [cmd_alsa_base, cmd_asound]
        return commands

    def start_command(self):
        return 'sudo /etc/init.d/shairport start %s' % (self.device_display_name)

    def stop_command(self):
        return 'sudo /etc/init.d/shairport stop'

    def restart_command(self):
        return 'sudo /etc/init.d/shairport restart %s' % (self.device_display_name)

    def restart(self):
        commands = self.copy_config_file_commands()
        print "Copying config files..."
        print self.run_commands(commands)
        commands = ['reboot']
        print "Running restart command"
        print self.run_commands(commands)
