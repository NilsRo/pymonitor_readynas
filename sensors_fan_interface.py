import shlex, subprocess, re

sensors_command = "/usr/bin/sensors"

fans_match = re.compile(r"fan3:\s+([0-9]+)\s+RPM")

def run_sensors(cmd):
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    oput = proc.stdout.read().decode("utf-8")
    
    fans = fans_match.search(oput, re.MULTILINE)

    try:
        return "FAN: " + fans.groups(0)[0] + " RPM"
    except AttributeError:
        return "FAN: error"

def get_sensors_info():
    return run_sensors(sensors_command)

def get_text():
    return [get_sensors_info()]

def get_update_freq():
    return 15

if __name__ == "__main__":
    print(get_sensors_info())

