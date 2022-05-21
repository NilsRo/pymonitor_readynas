import shlex, subprocess, re

sensors_command = "/usr/bin/sensors"

temp_match = re.compile(r"temp.*?\+([0-9.]+).*?C.*?\(.*?sensor \= thermal diode")

def run_sensors(cmd):
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    oput = proc.stdout.read().decode("utf-8")
    
    tems = temp_match.findall(oput, re.MULTILINE)

    a = set()
    for idx,temp in enumerate(tems):
        label = "TEMP"
        if idx == 0:
            label = "TEMP/CPU"
        if idx == 1:
            label = "TEMP/ICH"
        if idx == 2:
            label = "TEMP/SYS"
        try:
            a.add("%s: %s'C" % (label, temp))
        except AttributeError:
            pass

    return(sorted(a))

def get_sensors_info():
    return run_sensors(sensors_command)

def get_text():
    return get_sensors_info()

def get_update_freq():
    return 15

if __name__ == "__main__":
    print(get_sensors_info())

