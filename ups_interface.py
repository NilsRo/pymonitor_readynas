import shlex, subprocess
import re
import collections

ups_entry = collections.namedtuple("ups_entry", "name ip batt flags")

def get_status():
    fd = open("/etc/nut/upsmon.conf", "r")
    upsmon = fd.read().split('\n')
    fd.close()

    ups_dict = dict()

    # MONITOR ups@192.168.111.179 1 nut weehaznuts slave

    for line in upsmon:
        device = re.findall(r"MONITOR\s+(\S+)\s+", line)
        if not device:
            continue

        ups_full = device[0]
        ups_name = ups_full.split('@')[0]
        ups_addr = ups_full.split('@')[-1]

        if not ups_addr or ups_addr == ups_full:
            ups_name = ups_full
            ups_addr = 'localhost'

        args = shlex.split("upsc %s" % ups_full)
        upsc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        oput = upsc.stdout.read().decode("utf-8").split('\n')

        ups_batt = ''
        ups_flag = ''

        for ups_line in oput:
            k = ups_line.split(':')[0]
            v = ups_line.split(':')[-1].strip()

            if k == 'battery.charge':
                ups_batt = v

            if k == 'ups.status':
                ups_flag = v

        if not ups_batt:
            ups_batt = -1

        if not ups_flag:
            ups_flag = 'UNKN'

        if ups_addr != '127.0.0.1' and ups_addr != 'localhost':
            ups_flag = ups_flag + ' REMOTE'
        else:
            ups_flag = ups_flag + ' LOCAL'

        entry = ups_entry(ups_name, ups_addr, ups_batt, ups_flag)
        ups_dict[entry.name] = entry

    return ups_dict

def get_text():
    ups_db = get_status()

    if len(ups_db) == 0:
        return []

    ret = []
    for name, rdev in ups_db.items():
        ret.append("%s %s%% %s" % ('UPS' if rdev.name == 'ups' else "UPS %s" % rdev.name, rdev.batt, rdev.flags))
    
    return ret

if __name__ == "__main__":
    print(get_text())

