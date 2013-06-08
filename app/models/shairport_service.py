from app.lib import Service
from app.lib import util

class ShairportService(Service):

    config_file = 'shairport.config'
    default_contents = 'AirPlaySpeaker'

    @classmethod
    def namespace(cls):
        return 'shairport'

    @classmethod
    def display_name(cls):
        raise 'Shairport Airplay Service'

    def update_from_form(self, form):
        from app.models import DeploySetting
        ds = DeploySetting.find_or_create_by_namespace_key(ShairportService.namespace(), 'speaker_name')
        speaker_name = util.filter_empty(form.get('speaker_name'), self.default_contents)
        speaker_name = util.slugify(speaker_name, force_lowercase=False)
        if (speaker_name != self.get()):
            print "Saved new speaker name. <old: %s, new: %s>" % (self.get(), speaker_name)
            ds.value = speaker_name
            ds.save()
            self.set(value=ds.value)
            self.save()

        return True

    @property
    def speaker_name(self):
        return util.filter_empty(self.get(), self.default_contents)

    def start_command(self):
        return '/etc/init.d/shairport start %s' % (self.speaker_name)

    def stop_command(self):
        return '/etc/init.d/shairport stop'

    def restart_command(self):
        return '/etc/init.d/shairport restart %s' % (self.speaker_name)
