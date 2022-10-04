import shlex, subprocess
import re
import collections

df_entry = collections.namedtuple("df_entry", "name size size_unit used used_unit avail avail_unit used_percent mnt")

def get_status():
    cmd = "df -h"
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    oput = proc.stdout.read().decode("utf-8")

    df_dict = dict()

    for device in re.findall(r"(\S+)\s+([0-9\.]+)(\S)\s+([0-9\.]+)(\S)\s+([0-9\.]+)(\S)\s+(\S+)%\s+(/srv/\S+)\n", oput):
        entry = df_entry(device[0], device[1], device[2], device[3], device[4], device[5], device[6], device[7], device[8])
    
        df_dict[entry.name] = entry

    return df_dict

def get_text():
    df_db = get_status()

    if len(df_db) == 0:
        return []

    ret = []
    for name, rdev in df_db.items():
        if len(df_db) == 1:
            ret_name = "RAID"
        else:
            ret_name = name.split('/')[-1]

        ret_used = rdev.used
        if len(ret_used) > 3 or float(ret_used) == round(float(ret_used)):
            ret_used = str(int(round(float(ret_used),0)))
        if rdev.used_unit != rdev.size_unit:
            ret_used = ret_used + rdev.used_unit

        ret_size = rdev.size
        if len(ret_size) > 3 or float(ret_size) == round(float(ret_size)):
            ret_size = str(int(round(float(ret_size),0)))
        ret_size = ret_size + rdev.size_unit

        ret_percent = rdev.used_percent
        if ret_percent == 100:
            ret_percent = 'FULL!'
        else:
            ret_percent = "%s%%" % ret_percent

        ret.append("%s: %s (%s/%s)" % (ret_name, ret_percent, ret_used, ret_size))
    
    return ret

if __name__ == "__main__":
    print(get_text())

