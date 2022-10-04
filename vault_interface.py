import re
import collections

vault_entry = collections.namedtuple("vault_entry", "name fstype src dest mounted")

def get_status():
    fd = open("/proc/mounts", "r")
    mounts = fd.read()
    fd.close()

    fd = open("/etc/fstab", "r")
    fstab = fd.read().split('\n')
    fd.close()

    vault_dict = dict()

    for line in fstab:
        device = re.findall(r"(\S+)\s+(\S+)\s+(\S+)\s+.*?", line)
        if not device:
            continue

        fs_src = device[0][0]
        fs_dest = device[0][1]
        fs_type = device[0][2]
        name = fs_dest.split('/')[-1]

        if re.findall(r"^encfs", fs_src) and fs_type == 'fuse':
            fs_src = fs_src.split('#')[-1]
            fs_type = 'encfs'


        if re.findall(fs_dest, mounts):
            fs_mount = True
        else:
            fs_mount = False

        if fs_type in ('encfs','ecryptfs'):
            entry = vault_entry(name, fs_type, fs_src, fs_dest, fs_mount)
            vault_dict[entry.name] = entry

    return vault_dict

def get_text():
    vault_db = get_status()

    if len(vault_db) == 0:
        return []

    ret = []
    for name, rdev in vault_db.items():

        ret.append("%s IS %s" % (rdev.name.upper(), 'OPEN' if rdev.mounted else 'LOCKED'))
    
    return ret

if __name__ == "__main__":
    print(get_text())

