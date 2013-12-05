from app.lib import Service
from app.lib import util
import subprocess

class SystemStatusService(Service):

    config_file = 'system_status.config'
    default_contents = ''

    hdd_device_path = ''
    hdd_type = ''
    hdd_total = 0
    hdd_used = 0
    hdd_free = 0
    hdd_percent_consumed = ''
    hdd_mountpoint = ''

    mem_total = 0
    mem_free = 0
    mem_used = 0

    @classmethod
    def namespace(cls):
        return 'systemstatus'

    @property
    def display_name(self):
        raise 'System Status Reporting'

    def query_system(self):
        self.update_hdd_capacity()
        self.update_memory()


    def update_from_system(self):
        """Gets the result from several system commands and updates the DB"""
        return True

    def software_update(self):
        cmd = "git --git-dir=/sites/setitoff/.git --work-tree=/sites/setitoff/ pull origin release"
        output = subprocess.check_output(cmd, shell=True)
        cmd = "sudo chown -R pi:pi /sites"
        output += subprocess.check_output(cmd, shell=True)
        return output

    def update_memory(self):
        from app.models import DeploySetting
        cmd = "free -k | grep Mem"
        res = subprocess.check_output(cmd, shell=True)
        data = res.split()
        print cmd
        print data
        self.mem_total, self.mem_used, self.mem_free = int(data[1]), int(data[2]), int(data[3])
        
        keys = {'mem_total': self.mem_total,
                'mem_used': self.mem_used,
                'mem_free': self.mem_free }

        for k, v in keys.iteritems():
            ds = DeploySetting.find_or_create_by_namespace_key(SystemStatusService.namespace(), k)
            ds.value = v
            ds.save()
        return True

    def update_hdd_capacity(self):
        from app.models import DeploySetting
        cmd = "df -lT | grep ext4"
        res = subprocess.check_output(cmd, shell=True)
        data = res.split()
        print cmd
        print data
        self.hdd_device_path, self.hdd_type, self.hdd_total, self.hdd_used, self.hdd_free, self.hdd_percent_consumed, self.hdd_mountpoint = data
        self.hdd_total, self.hdd_used, self.hdd_free = int(self.hdd_total), int(self.hdd_used), int(self.hdd_free)
        keys = {'hdd_device_path': self.hdd_device_path,
                'hdd_type': self.hdd_type,
                'hdd_total': self.hdd_total,
                'hdd_used': self.hdd_used,
                'hdd_free': self.hdd_free,
                'hdd_percent_consumed': self.hdd_percent_consumed,
                'hdd_mountpoint': self.hdd_mountpoint }

        for k, v in keys.iteritems():
            ds = DeploySetting.find_or_create_by_namespace_key(SystemStatusService.namespace(), k)
            ds.value = v
            ds.save()
        return True
