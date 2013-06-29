from app.lib import Service
from app.lib import util
from path import path

APP_PATH = '/sites/set-it-off'

class WifiService(Service):

    config_file = 'wifi.config'
    default_contents = ''

    profiles = ['original', 'wep', 'wpa']
    profile = None
    essid = None
    password = None
    protocol = None
    key_mgmt = None
    pairwise = None
    scan_ssid = None

    @classmethod
    def namespace(cls):
        return 'wifi'

    @property
    def display_name(self):
        raise 'WiFi Radio'


    def update_from_system(self):
        """Gets the result from several system commands and updates the DB"""
        return True

    def save_config_to_disk(self):
        if self.profile is None:
            print "No profile set. Cannot save config."
            return None
        if self.profile == 'original':
            self.save_original_config_to_disk()
        elif self.profile == 'wep':
            self.save_wep_config_to_disk(self.essid, self.password)
        elif self.profile == 'wpa':
            self.save_wpa_config_to_disk(self.essid, self.password)
        else:
            print "Config profile %r not found! Cannot save." % self.profile

    def save_original_config_to_disk(self):
        src = path(APP_PATH + '/profiles/network-interfaces/interfaces.original')
        target = path('/etc/network/interfaces')
        cmd = "cp %s %s" % (src, target,)
        print "Restoring original WiFi interfaces Configuration..."
        self.run_commands([cmd])

    def save_wep_config_to_disk(self, essid, password=None):
        src = path(APP_PATH + '/profiles/network-interfaces/interfaces.wep')
        target = path('/etc/network/interfaces')
        
        wep_config = """

wireless-essid %s
wireless-key s:%s
""" % (essid, password,)

        if password is None:
            wep_config = """

wireless-essid %s
""" % (essid)
        
        print "Restoring WEP WiFi interfaces Configuration..."
        wep_config_source = src.text()
        wep_config_source += wep_config
        target.write_text(wep_config_source)

    def save_wpa_config_to_disk(self, essid, password, protocol='RSN', key_mgmt='WPA-PSK', pairwise='CCMP TKIP', scan_ssid='1'):
        src = path('profiles/network-interfaces/interfaces.wpa2')
        target = path('/etc/network/interfaces')
        cmd = "cp %s %s" % (src, target,)
        print "Restoring WPA WiFi interfaces Configuration..."
        self.run_commands([cmd])

        wpa_config = """
network={
ssid="%s"
scan_ssid=%s
proto=%s
key_mgmt=%s
pairwise=%s
psk="%s"
}
""" % (essid, scan_ssid, protocol, key_mgmt, pairwise, password)
        wpa_target = path('/etc/wpa_supplicant/wpa_supplicant.conf')
        wpa_target.write_text(wpa_config)

