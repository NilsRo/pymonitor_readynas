import shlex, subprocess, re, time, sys

snapraid_command = "snapraid status"

snapraid_busy = re.compile(r"SnapRAID is already in use")

snapraid_match = re.compile(r"[0-9]*:\s*(\S*)\s*inet\s*([0-9.]*)")
snapraid_line = re.compile(r"---------------")
snapraid_stats = re.compile(r"\s*([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.%]+)\s*")
snapraid_no_sync = re.compile(r"No sync is in progress")
snapraid_no_rehash = re.compile(r"No rehash is in progress or needed")
snapraid_no_error = re.compile(r"No error detected")

def run_snapraid(cmd):
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.read().decode("utf-8")
    stderr = proc.stderr.read().decode("utf-8")
    retcode = proc.poll()

    has_errors = False
    try:
        time.sleep(1)
        if retcode > 0:
            has_errors = True
    except Exception:
        # this happends sometimes (TypeError: '>' not supported between instances of 'NoneType' and 'int') - maybe a raid
        sys.stderr.write("WARNING: Unable to get snapraid command exit code")

    if has_errors:
        return([]) # no snapraid - don't spam me

    if snapraid_busy.search(stderr):
        return(["sRAID is active!"])

    ret = set()
    in_summary = False

    for ll in stdout.split("\n"):
        if snapraid_line.search(ll):
            in_summary = True

        summary = snapraid_stats.search(ll)
        if in_summary and summary:
            ret.add("sRAID: %sGB free"%summary.group(6))
            ret.add("sRAID: %s used"%summary.group(7))
            ret.add("sRAID: %s files"%summary.group(1))

    no_sync = snapraid_no_sync.search(stdout)
    no_rehash = snapraid_no_rehash.search(stdout)
    no_error = snapraid_no_error.search(stdout)

    if not no_sync:
        ret.add("sRAID: needs sync!") 

    if not no_rehash:
        ret.add("sRAID: needs rehash!") 

    if not no_error:
        ret.add("sRAID: has errors!")

    if no_sync and no_rehash and no_error:
        ret.add("sRAID: is healthy")

    return sorted(ret)

def get_snapraid_info():
    return run_snapraid(snapraid_command)

def get_text():
    return get_snapraid_info()

def get_update_freq():
        return 1800 # every 30 minutes is more than enough, the same setting as in interface
                    # https://192.168.1.22/#/storage/smart/settings

if __name__ == "__main__":
    print(get_snapraid_info())

