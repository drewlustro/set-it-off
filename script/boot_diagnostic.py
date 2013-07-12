#!/usr/bin/env python

import sys
sys.path.append("/sites/set-it-off")

import subprocess
from app.models import WifiService

def hr(size=40):
    text = ['-' for x in xrange(size)]
    text = ''.join(text)
    print text

def br(size=1):
    for i in xrange(size):
        print

def get_device_ip(device):
    global ip_addresses
    try:
        cmd = 'ifconfig %s | grep "inet addr"' % device
        res = subprocess.check_output(cmd, shell=True)
        data = res.split()
        ip = data[1].split(':')[1]
        if ip:
            ip_addresses[device] = ip
            return ip
    except subprocess.CalledProcessError:
        return "(invalid device)"
    except IndexError:
        return "(not found)"
    return None

def request_value_with_options(question, options=None):
    if options is None:
        question = "%s (or enter 'x' to cancel:) " % (question)
        options = []
    else:
        question = "%s %r (or enter 'x' to cancel): " % (question, options)
    while True:
        res = raw_input(question)
        if res == 'x' or res == '':
            return None
        if res in options:
            return res
        if not options or len(options) <= 0:
            return res
        print "[Error] Invalid input '%s'. Please choose from the available options in brackets." % (res, )

br()
hr()
hr()
print "PAULPI DIAGNOSTIC SERVICE (v0.1)"
hr()
hr()
br()

interfaces = ['eth0']
ip_addresses = {}

config_param_keys = ['essid', 'wifi_password', 'wifi_profile']
config_param_descriptions = {'essid': 'WiFi Network Name',
                            'wifi_password': 'WiFi Network Password',
                            'wifi_profile': 'WiFi Router Security Mode'}

config_param_options = {'essid': None,
                        'wifi_password': None,
                        'wifi_profile': ['wpa', 'wep', 'original'] }

config_param_questions = {'essid': 'What is the name of your WiFi Network?',
                        'wifi_password': 'What is the password to your WiFi network?',
                        'wifi_profile': 'What is the WiFi security mode of your router?'}

config_param_values = {}
#for iface in interfaces:
#    print "Interface %s IP Address: %s" % (iface, get_device_ip(iface),)

for iface, ip in ip_addresses.iteritems():
    hr()
    print "IP ADDRESS: %s" % ip
    print "ADMIN PANEL ADDRESS: http://%s/" % ip
    hr()

br()

do_software_update = request_value_with_options('Do software update?', ['yes', 'no'])
if do_software_update == 'yes':
    cmd = "git --git-dir=/sites/set-it-off/.git --work-tree=/sites/set-it-off/ pull origin release"
    br()
    print "SOFTWARE UPDATE"
    hr()
    output = subprocess.check_output(cmd, shell=True)
    print output
    hr()

br()


do_wifi_setup = request_value_with_options('Perform WiFi setup?', ['yes', 'no'])
if do_wifi_setup == 'yes':
    br()
    print "WIFI SETUP"
    hr()
    for p in config_param_keys:
        res = request_value_with_options(config_param_questions[p],\
                                         config_param_options[p])
        if res is not None:
            config_param_values[p] = res
    hr()
    #print "Collected values:"
    #print config_param_values

    wifi_service = WifiService()
    wifi_service.essid = config_param_values['essid']
    wifi_service.password = config_param_values['wifi_password']
    wifi_service.profile = config_param_values['wifi_profile']

    should_write = request_value_with_options('Write these values to disk?', ['yes', 'no'])
    if should_write == 'yes':
        wifi_service.save_config_to_disk()
        print "Saved new WiFi configuration. Please reboot to take effect."
    else:
        print "Did not save new config to disk."

br()
hr()
print "PaulPi diagnostic shell finished. Goodbye."
hr()
br()
br()


