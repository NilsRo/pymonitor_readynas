import shlex, subprocess, re

ip_command = "/sbin/ip -o -f inet addr"

ip_match = re.compile(r"[0-9]*:\s*(\S*)\s*inet\s*([0-9.]*)")
temp_match = re.compile(r"temp.*?\+([0-9\.]*).*?C.*\(.*sensor \= CPU diode")

def run_uptime(cmd):
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return "UP: %s days" % (round(uptime_seconds/86400,2))

def get_uptime_info():
    return run_uptime(ip_command)

def get_text():
    return [get_uptime_info()]

if __name__ == "__main__":
    print(get_uptime_info())

