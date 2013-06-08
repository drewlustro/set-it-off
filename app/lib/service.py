from path import path

class Service:

    namespace = 'global'
    config_file = 'service.config'
    default_contents = 'DefaultConfigContents'

    def __init__(self):
        from app import config
        self.filepath = path('%s/%s' % (config.SERVICE_CONFIG_DIR, self.config_file))
        self.data = {}
        self.load_from_file()

    def init_default_file(self):
        self.filepath.write_text(self.default_contents)

    def set(self, key='__plaintext', value=''):
        self.data[key] = value

    def get(self, key='__plaintext'):
        return self.data[key]

    def update_from_form(self, form):
        return True

    def save(self):
        if (self.data['__plaintext']):
            return self.filepath.write_text(self.data['__plaintext'])

    def load_from_file(self):
        try:
            filetext = self.read()
            if filetext:
                print "Loaded from File: '%r'" % filetext
                self.data['__plaintext'] = filetext
        except IOError as e:
            print "Init default file for %r" % (self)
            self.init_default_file()
            self.load_from_file()


    def read(self):
        return self.filepath.text()

    def __repr__(self):
        return '<%s> data: %r' % (self.__class__.__name__, self.data, )