import shlex, subprocess

smart_ctl_command = "/usr/sbin/smartctl -q silent -n standby -H -d sat"

#disks = "/var/disks/front_tray/0", "/var/disks/front_tray/1", "/var/disks/front_tray/2", "/var/disks/front_tray/3", "/var/disks/front_tray/4"

# /dev/disk/by-path/pci-0000:00:1f.2-ata-1 <-- DOM disk, ignore
disks = "/dev/disk/by-path/pci-0000:00:1f.2-ata-2", "/dev/disk/by-path/pci-0000:00:1f.2-ata-3", "/dev/disk/by-path/pci-0000:00:1f.2-ata-4", "/dev/disk/by-path/pci-0000:00:1f.2-ata-5", "/dev/disk/by-path/pci-0000:00:1f.2-ata-6"

def run_smartctl(cmd):
    args = shlex.split(cmd)
    retcode = subprocess.call(args)

    if (retcode & 1 != 0):
        return "." # bit 1: open failed, no identify or in low-power mode
    elif (retcode & 2 != 0):
        return "z" # bit 2: /k. my disks return this in standby :)
    elif(retcode & 8 != 0):
        return "f" # bit 2: smart data read error or checksum error
    elif(retcode & 64 != 0):
        return "F" # bit 3: smart indicated failure
    elif(retcode & 128 != 0):
        return "o" # bit 4: prefail attributes threshold reached, status ok
    elif(retcode & 256 != 0):
        return "0" # bit 5: prefail attributes threshold reached, status bad
    elif(retcode & 512 != 0):
        return "!" # bit 6: device log contains errors
    elif(retcode & 1024 != 0):
        return "?" # bit 7: device self-test contains errors
    elif(retcode == 0):
        return "O" # all ok
    else:
        return "X"

def get_smart_info():
    ret = "Disks: ["

    for disk in disks:
        cmd = smart_ctl_command + " " + disk
        ret += run_smartctl(cmd)
    
    return ret + "]"

def get_text():
    return [get_smart_info()]

def get_update_freq():
    return 1800 # every 30 minutes is more than enough, the same setting as in interface
                # https://192.168.1.22/#/storage/smart/settings

if __name__ == "__main__":
    print(get_smart_info())

