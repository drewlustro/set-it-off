from path import path
import subprocess

class Service:

    namespace = 'global'
    config_file = 'service.config'
    default_contents = 'DefaultConfigContents'

    def __init__(self):
        from app import config
        self.filepath = path('%s/%s' % (config.SERVICE_CONFIG_DIR, self.config_file))
        self.data = {}
        self.load_config_from_file()
        self.update()

    @classmethod
    def display_name(cls):
        raise NotImplementedError('Undefined @property Service.display_name')

    @classmethod
    def namespace(cls):
        raise NotImplementedError('Undefined @classmethod Service.namespace()')

    def init_default_file(self):
        self.filepath.write_text(self.default_contents)

    def set(self, key='__plaintext', value=''):
        self.data[key] = value

    def get(self, key='__plaintext'):
        return self.data[key]

    def update(self):
        return self.update_from_system()

    def update_from_system(self):
        """Gets the result from several system commands and updates the DB"""
        return True

    def update_from_form(self, form):
        return True

    def save(self):
        if (self.data['__plaintext']):
            return self.filepath.write_text(self.data['__plaintext'])

    def load_config_from_file(self):
        try:
            filetext = self.read()
            if filetext:
                print "Loaded initial config from file: '%r'" % filetext
                self.data['__plaintext'] = filetext
        except IOError as e:
            print "Init default file for %r" % (self)
            self.init_default_file()
            self.load_config_from_file()

    def read(self):
        return self.filepath.text()

    def start(self):
        cmd = self.start_command()
        print "Running start command"
        print cmd
        return subprocess.call(cmd, shell=True)

    def stop(self):
        cmd = self.stop_command()
        print "Running stop command"
        print cmd
        return subprocess.call(cmd, shell=True)

    def restart(self):
        cmd = self.restart_command()
        print "Running restart command"
        print cmd
        return subprocess.call(cmd, shell=True)

    def start_command(self):
        return 'echo "This is a Service START command"'

    def stop_command(self):
        return 'echo "This is a Service STOP command"'

    def restart_command(self):
        return 'echo "This is a Service RESTART command"'

    def run_commands(self, commands):
        ret = []
        for cmd in commands:
            print "[%s RUN]: '%s'" % (self.__class__.__name__, cmd)
            ret.append(subprocess.call(cmd, shell=True))
        return ret

    def __repr__(self):
        return '<%s> data: %r' % (self.__class__.__name__, self.data, )
