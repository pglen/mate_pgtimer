#!/usr/bin/env python

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import sys, time, os, random, syslog, threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

try:
    gi.require_version('MatePanelApplet', '4.0')
    from gi.repository import MatePanelApplet
except:
    print("No Mate Panel subsystem")
    syslogx("No Mate Panel subsystem")

try:
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify
except:
    print("No notify subsystem")
    syslogx("No notify subsystem")

try:
    from playsound import playsound
except:
    print("No sound subsystem")
    syslogx("No sound subsystem")

# ------------------------------------------------------------------------

def syslogx(*vars):

    strx = ""
    for aa in vars:
        strx += str(aa) + " "

    syslog.syslog(strx)

def _asynsound():
    #print("Thread start")

    #Gdk.beep()

    playsound("/usr/share/sounds/freedesktop/stereo/complete.oga")
    playsound("/usr/share/sounds/freedesktop/stereo/complete.oga")

    #print("Thread end")

def play_sound():
    ttt = threading.Thread(None, _asynsound)
    ttt.start()

def _callback_func():
    syslog.syslog("Alarm Acknowledged")
    pass

def notify_sys(alname, alsub, tout = 0):
    try:
        Notify.init("Countdown")
    except:
        print("Notify subsystem is not installed")
        syslog.syslog("Notify subsystem is not installed")
        return

    nnn = Notify.Notification.new(alname, alsub, "dialog-information")
    #nnn.add_action("action_click", "Acknowledge Alarm", _callback_func, None)
    nnn.set_timeout(tout * 1000)
    nnn.show()

def put_exception(xstr):

    import traceback

    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    #put_debug(cumm)
    syslog.syslog("%s %s %s" % (xstr, a, b))

class Spacer(Gtk.HBox):

    def __init__(self, sp = None, bg = None):
        Gtk.HBox.__init__(self)
        if bg:
            self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(bg))
        if sp == None:
            sp = 6
        self.set_size_request(sp, sp)


class vertbar(Gtk.DrawingArea):

    def __init__(self, ww, hh, barcol):
        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        self.connect("draw", self.draw_event)
        self.set_size_request(ww, hh)
        self.barcol = barcol
        self.highcol = (0,1,1)
        self.cent = 0

    def set_procent(self, cent, barcol = (0,1,0)):
        if cent > 100: cent = 100
        if cent < 1: cent = 1
        self.highcol = barcol
        self.cent = cent

        self.queue_draw()

    def draw_event(self, pdoc, cr):
        rect = self.get_allocation()
        if rect.height < 0:
            return

        cr.set_source_rgba(*self.barcol)
        cr.rectangle( 1, 2, rect.width-2, rect.height-4)
        cr.fill()

        eff = rect.height-4
        hhh = self.cent * eff / 100
        #syslog.syslog("draw cent %d hhh %d" % (self.cent, hhh) )
        cr.set_source_rgba(*self.highcol)
        cr.rectangle( 1, eff-hhh, rect.width-2, hhh)
        cr.fill()

# EOF

