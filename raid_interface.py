import re
import collections

raid_entry = collections.namedtuple("raid_entry", "name status level drives size dev_name elements online_elements disks recovery sub_status")

def get_status():
    fd = open("/proc/mdstat", "r")
    txt = fd.read()
    fd.close()

    raid_dict = dict()

    for device in re.findall(r"(md[0-9]*) : (\S+) (\S+) (.*?)\n\s+?(\d+)\s+?blocks[^\[]+\[(\d+)\/(\d+)\]\s+\[(.*?)\]", txt):
        entry = raid_entry(device[0], device[1], device[2], [],
                device[4], "/dev/%s" % device[0], device[5], device[6], device[7], 0, False)
    
        raid_dict[entry.name] = entry

    for device in re.findall(r"(md[0-9]*) : .*?\n.*?\n.*? (recovery|check) =\s+([\d\.]+)%", txt):
        try:
            raid_dict[device[0]] = raid_dict[device[0]]._replace(sub_status=device[1],recovery=float(device[2]))
        except:
            pass

    return raid_dict

def get_text():
    raid_db = get_status()

    if len(raid_db) == 0:
        return []

    ret = []
    for name, rdev in raid_db.items():
        if len(raid_db) == 1:
            ret_name = "RAID"
        else:
            ret_name = name

        if rdev.status == "active":
            if rdev.recovery > 0 and rdev.sub_status == 'recovery':
                ret_status = "Recovery %s%%" % int(rdev.recovery)
            elif rdev.recovery > 0 and rdev.sub_status == 'check':
                ret_status = "Checking %s%%" % round(rdev.recovery,1)
            elif rdev.elements > rdev.online_elements:
                ret_status = "Degraded %s" % rdev.disks
            else:
                ret_status = "Healthy"
        else:
            ret_status = rdev.status

        ret.append(ret_name + ": " + ret_status)
    
    return ret

if __name__ == "__main__":
    print(get_text())

