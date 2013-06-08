from app.lib import Service
from app.lib import util

class ShairportService(Service):

    config_file = 'shairport.config'
    namespace = 'shairport'
    default_contents = 'AirPlay Speaker'

    def update_from_form(self, form):
        from app.models import DeploySetting
        ds = DeploySetting.find_or_create_by_namespace_key(self.namespace, 'speaker_name')
        speaker_name = util.filter_empty(form.get('speaker_name'), self.default_contents)
        speaker_name = util.slugify(speaker_name, force_lowercase=False)
        if (speaker_name != self.get()):
            print "Saved new speaker name. <old: %s, new: %s>" % (self.get(), speaker_name)
            ds.value = speaker_name
            ds.save()
            self.set(value=ds.value)
            self.save()

        return True

