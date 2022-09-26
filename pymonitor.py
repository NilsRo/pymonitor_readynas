#!/usr/bin/env python3.1

import os, re, socket
from importlib.machinery import SourceFileLoader
from daemon3x import daemon
from optparse import OptionParser
from threading import Thread
import time
import signal
import send_thecus
import gpio as GPIO

# Options
parser = OptionParser("usage: %prog [options]", version="%prog 2.0")
parser.add_option("-p", "--port", action="store", type="string", dest="port",
        default="/dev/ttyS1", metavar="PORT", help="communicate with AVR on PORT")
parser.add_option("-D", "--daemon", action="store_true", dest="daemon",
        default=False, help="daemonize")
parser.add_option("-d", action="store_true", dest="debug",
        default=False, help="debug")
parser.add_option("--pid-file", action="store", type="string", dest="pidfile",
        default="/tmp/pymonitor.pid", help="pid-file location")
parser.add_option("--update-freq", action="store", type="int", dest="updatefreq",
        default=15, help="number of seconds before requesting modules to update their output")
parser.add_option("--screen-time", action="store", type="int", dest="screentime",
        default=5, help="number of seconds each slide is being displayed on LCD (up to 60)")
opts, args = parser.parse_args()

advance_in = opts.screentime
if advance_in > 60:
    advance_in = 60

get_text = "get_text"
get_update_freq = "get_update_freq"
default_update_freq = opts.updatefreq

ev_refresh_now = False
ev_pause = False
ev_next = False
ev_back = False

# build a list of modules
# the stagger value causes module updates to be staggered
stagger = 0
mod_dir = os.path.dirname(os.path.realpath(__file__))
mods = []
for file in os.listdir(mod_dir):
    match = re.match(r"^(\S*)_interface.py$", file)
    if match:
        fname = os.path.join(mod_dir, file)
        mname = match.groups(0)[0]
        #mod = imp.load_source(mname, fname)
        mod = SourceFileLoader(mname, fname).load_module()

        mod_desc = { "name": mname, "mod": mod }
        if get_text in dir(mod):
            mod_desc[get_text] = mod.get_text
        else:
            mod_desc[get_text] = None

        if get_update_freq in dir(mod):
            mod_desc[get_update_freq] = mod.get_update_freq()
        else:
            mod_desc[get_update_freq] = default_update_freq

        mod_desc[get_update_freq] = mod_desc[get_update_freq] + stagger
        stagger = stagger + 1

        mod_desc["text"] = None
        mod_desc["countdown"] = 0
        mods.append(mod_desc)

def buttons_loop():
    global ev_next, ev_back, ev_refresh_now, ev_pause

    GPIO.setup(16, GPIO.IN)
    GPIO.setup(17, GPIO.IN)
    GPIO.setup(18, GPIO.IN)
    GPIO.setup(19, GPIO.IN)

    st_esc = 1
    st_ent = 1
    st_dwn = 1
    st_upp = 1

    while run:
        ev_esc = GPIO.input(16)
        ev_ent = GPIO.input(17)
        ev_dwn = GPIO.input(18)
        ev_upp = GPIO.input(19)

        if ev_esc == 0 and st_esc == 1:
            if opts.debug == True:
                print("Escape pressed!")
            ev_refresh_now = True

        if ev_ent == 0 and st_ent == 1:
            if opts.debug == True:
                print("Enter pressed!")
            if ev_pause:
                ev_pause = False
            else:
                ev_pause = True

        if ev_upp == 0 and st_upp == 1:
            if opts.debug == True:
                print("Up pressed!")
            ev_back = True
            ev_pause = True

        if ev_dwn == 0 and st_dwn == 1:
            if opts.debug == True:
                print("Down pressed!")
            ev_next = True
            ev_pause = True

        st_esc = ev_esc
        st_ent = ev_ent
        st_dwn = ev_dwn
        st_upp = ev_upp

        time.sleep(0.1)

def sigterm_handler(_signo, _stack_frame):
    global run
    for seq in [3, 2, 1, 0]:
        send_thecus.write_message(msg1 = "", msg2 = "   Shutdown (%s)   " % seq, port = opts.port)
        time.sleep(1)
    send_thecus.write_message(msg1 = "", msg2 = "", port = opts.port)
    run = False

def main_loop():

    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    global ev_next, ev_back, ev_refresh_now, ev_pause
    idx = 0
    sub_idx = 0

    while run:
        # run gettext for each required module
        for mod in mods:
            if mod["countdown"] == 0 or ev_refresh_now:
                if mod[get_text] != None:
                    mod["text"] = mod[get_text]()
                else:
                    mod["text"] = []
                mod["countdown"] = mod[get_update_freq]
            else:
                mod["countdown"] = mod["countdown"] - 1

        ev_refresh_now = False

        # build the time string
        t = time.localtime(time.time())
        t_msg = time.strftime(" %H:%M:%S")

        if ev_pause and t.tm_sec % advance_in == 0:
            t_msg = " <<HOLD>>"

        msg1 = socket.gethostname().ljust(11)[0:11] + t_msg

        # if zero-length mods, blank second line
        if len(mods) == 0:
            msg2 = ""
        else:
            if ev_back:
                if sub_idx == 0:
                    idx = idx - 1
                else:
                    sub_idx = sub_idx - 1

                if idx < 0:
                    idx = len(mods) - 1

                ev_back = False

            if ev_next:
                sub_idx = sub_idx + 1
                ev_next = False

            if opts.debug:
                print("D: idx: %s sub-idx: %s"%(idx,sub_idx))

            # See if we've exceeded the sub index
            while sub_idx >= len(mods[idx]["text"]) or mods[idx]["text"][sub_idx] == None:
                sub_idx = 0
                idx = idx + 1

                # See if we've exceeded the index
                if idx >= len(mods):
                    idx = 0

            # Load the string
            msg2 = mods[idx]["text"][sub_idx]

            # Increment counter for next run
            if t.tm_sec % advance_in == 0 and not ev_pause:
                sub_idx = sub_idx + 1

        ## Display the messages
        if opts.debug == True:
            print(msg1)
            print(msg2)
            print()
        else:
            send_thecus.write_message(msg1 = msg1, msg2 = msg2,
                    port = opts.port)

        time.sleep(1)


class MyDaemon(daemon):
    def run(self):
        main_loop()

run = True

monitor_thread = Thread(target=buttons_loop)
monitor_thread.start()

if opts.daemon == True:
    d = MyDaemon(opts.pidfile)
    d.start()
else:
    main_loop()

monitor_thread.join()

