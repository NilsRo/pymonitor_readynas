import shlex, subprocess, re

def run_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return "UP: %s days" % (round(uptime_seconds/86400,2))

def get_uptime_info():
    return run_uptime()

def get_text():
    return [get_uptime_info()]

if __name__ == "__main__":
    print(get_uptime_info())

