#!/usr/bin/env python

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import sys, time, os, random, syslog, threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

realinc = os.path.realpath(os.path.dirname(__file__))
sys.path.append(realinc)

# ------------------------------------------------------------------------

# Supporting routines
from support import *

# Globals

inst_arr     = []
was_inst     = 0

def apply_screen_coord_correction(self, x, y, widget, relative_widget):

    corrected_y = y; corrected_x = x
    rect = widget.get_allocation()
    screen_w = Gdk.Screen.width()
    screen_h = Gdk.Screen.height()
    delta_x = screen_w - (x + rect.width)
    delta_y = screen_h - (y + rect.height)
    if delta_x < 0:
        corrected_x += delta_x
    if corrected_x < 0:
        corrected_x = 0
    if delta_y < 0:
        corrected_y = y - rect.height - relative_widget.get_allocation().height
    if corrected_y < 0:
        corrected_y = 0
    return [corrected_x, corrected_y]

def _done_about(widget, win):
    win.destroy()

def about_dialog(widget, win):

    try:
        win = Gtk.Window()
        win.connect('destroy', Gtk.main_quit)
        win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        vbox = Gtk.VBox()
        vbox.pack_start(Gtk.Label(" "), 1,1,2)
        lab = Gtk.Label("       PG Timer Applet        ")
        vbox.pack_start(lab, 1,1,2)
        vbox.pack_start(Gtk.Label(" "), 1,1,2)

        lab2 = Gtk.Label("       Written by Peter Glen        ")
        vbox.pack_start(lab2, 1,1,2)
        #vbox.pack_start(Gtk.Label(" "), 1,1,2)
        vbox.pack_start(Spacer(), 1,1,2)
        hbox = Gtk.HBox()
        bbb = Gtk.Button.new_with_mnemonic(" _OK ");
        bbb.connect("clicked", _done_about, win)
        hbox.pack_start(Gtk.Label(" "), 1,1,2)
        hbox.pack_start(bbb, 1,1,2)
        hbox.pack_start(Gtk.Label(" "), 1,1,2)
        vbox.pack_start(hbox, 1,1,2)
        vbox.pack_start(Spacer(), 1,1,2)

    except:
        put_exception("about_dialog():")
        pass
    win.add(vbox)
    win.show_all()
    Gtk.main()


def show_msg(widget, msg="Empty Message", event=None):

    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    hbox = Gtk.VBox()
    hbox.pack_start(Gtk.Label(" "), 1,1,2)
    lab = Gtk.Label(msg)
    hbox.pack_start(lab, 1,1,2)
    hbox.pack_start(Gtk.Label(" "), 1,1,2)

    lab2 = Gtk.Label("       Written by Peter Glen        ")
    hbox.pack_start(lab2, 1,1,2)
    hbox.pack_start(Gtk.Label(" "), 1,1,2)

    win.add(hbox)
    win.show_all()
    Gtk.main()

def _make_line(num, val):

    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label(" "), 1,1,2)

    hbox.lab1 = Gtk.Label("Timer %d:   " % (num+1))
    hbox.pack_start(hbox.lab1, 1,1,2)

    hbox.check3 = Gtk.CheckButton.new_with_label("Enable Sound"); hbox.check3.set_active(True)
    hbox.pack_start(hbox.check3, 1,1,2)

    hbox.check3 = Gtk.CheckButton.new_with_label("Enable Notify"); hbox.check3.set_active(True)
    hbox.pack_start(hbox.check3, 1,1,2)

    hbox.lab2 = Gtk.Label("  Timeout: (hh:mm:ss)    ")
    hbox.pack_start(hbox.lab2, 1,1,2)

    #hbox.text1 = Gtk.Entry(); hbox.text1.set_width_chars(5)
    #hbox.pack_start(hbox.text1, 1,1,2)

    hbox.text1 = Gtk.SpinButton.new_with_range(0, 24, 1);
    hbox.pack_start(hbox.text1, 1,1,2)

    hbox.text2 = Gtk.SpinButton.new_with_range(0, 59, 1);
    hbox.pack_start(hbox.text2, 1,1,2)

    hbox.text3 = Gtk.SpinButton.new_with_range(0, 59, 1);
    hbox.text3.set_value(val)
    hbox.pack_start(hbox.text3, 1,1,2)

    hbox.pack_start(Gtk.Label(" "), 1,1,2)
    return hbox

# ------------------------------------------------------------------------

def _done_config(butt, win, applet):

    syslogx("OK", butt, win.buttarr, applet)

    cnt = 0
    for aa in win.buttarr:
        syslogx("arr", cnt, aa)
        syslogx("val", aa.text1.get_value(),
                aa.text2.get_value(),  aa.text3.get_value())

    win.destroy()

# ------------------------------------------------------------------------

def config_timer(widget, applet):

    syslogx("more ", widget, applet)

    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    win.buttarr = []

    vbox = Gtk.VBox()

    vbox.pack_start(Spacer(12), 0, 0, 0)

    try:
        for aa in range(4):
            #vbox.pack_start(Gtk.Label("  "), 1,1,2)
            hbox = _make_line(aa, applet.setarr[aa])
            vbox.pack_start(hbox, 1,1,2)
            win.buttarr.append(hbox)

        vbox.pack_start(Spacer(), 0, 0, 0)

        bbox = Gtk.HBox()
        bbb = Gtk.Button.new_with_mnemonic(" _Save / _OK ");
        bbb.connect("clicked", _done_config, win, applet)

        bbox.pack_start(Gtk.Label(" "), 1, 1, 2)
        bbox.pack_start(bbb, 1, 1, 2)
        bbox.pack_start(Gtk.Label(" "), 1, 1, 2)
        vbox.pack_start(bbox, 1,1,2)

        vbox.pack_start(Spacer(), 0, 0, 0)

    except:
        put_exception("config_timer():")

    win.add(vbox)
    win.show_all()
    Gtk.main()

def _done_hist(butt, win, applet):

    syslogx("OK", butt, win.buttarr, applet)

    cnt = 0
    for aa in win.buttarr:
        syslogx("arr", cnt, aa)
        syslogx("val", aa.text1.get_value(),
                aa.text2.get_value(),  aa.text3.get_value())

    win.destroy()

# ------------------------------------------------------------------------

def hist_timer(widget, applet):

    syslogx("more ", widget, applet)

    win = Gtk.Window()
    win.connect('destroy', Gtk.main_quit)
    win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    win.buttarr = []

    vbox = Gtk.VBox()

    vbox.pack_start(Spacer(12), 0, 0, 0)

    try:
        bbox = Gtk.HBox()
        bbb = Gtk.Button.new_with_mnemonic(" _OK ");
        bbb.connect("clicked", _done_hist, win, applet)

        bbox.pack_start(Gtk.Label(" "), 1, 1, 2)
        bbox.pack_start(bbb, 1, 1, 2)
        bbox.pack_start(Gtk.Label(" "), 1, 1, 2)
        vbox.pack_start(bbox, 1,1,2)

        vbox.pack_start(Spacer(), 0, 0, 0)

    except:
        put_exception("hist_timer():")

    win.add(vbox)
    win.show_all()
    Gtk.main()

# ------------------------------------------------------------------------

def _timer_all(num):
    syslogx("timer started ", num,  os.getpid(), time.ctime())
    global inst_arr
    for aa in inst_arr:
        if aa:
            rnum = num + 1
            aa.timerarr[num] = aa.setarr[num]
            aa.timerlab.set_text("Timer %d" % rnum)
            notify_sys("Timer Started", "Timer Number %d at %s" % (rnum, time.ctime()), 5)

def start_timer1(widget, event=None):
    _timer_all(0)

def start_timer2(widget, event=None):
    _timer_all(1)

def start_timer3(widget, event=None):
    _timer_all(2)

def start_timer4(widget, event=None):
    _timer_all(3)

# ------------------------------------------------------------------------

def append_menu(applet):

    menu_xml="""
        <menuitem item="Item 1" action="AboutAction"/>
        <menuitem item="Item 2" action="TimerAction"/>
        <menuitem item="Item 3" action="HistAction"/>
        <menuitem item="Item 4" action="Start1Action"/>
        <menuitem item="Item 5" action="Start2Action"/>
        <menuitem item="Item 6" action="Start3Action"/>
        <menuitem item="Item 7" action="Start4Action"/>
    """

    actions = [
        ('AboutAction', None, 'About Timer Applet', None, None, about_dialog),
        ('TimerAction', None, 'Configure Timers', None, None, config_timer),
        ('HistAction', None, 'History of Timers', None, None, hist_timer),
        ('Start1Action', None, 'Start Timer 1', None, None, start_timer1),
        ('Start2Action', None, 'Start Timer 2', None, None, start_timer2),
        ('Start3Action', None, 'Start Timer 3', None, None, start_timer3),
        ('Start4Action', None, 'Start Timer 4', None, None, start_timer4),
        ]
    action_group = Gtk.ActionGroup.new("Timer")
    action_group.add_actions(actions, applet)
    applet.setup_menu(menu_xml, action_group)


def applet_fill(applet):

    # you can use this path with gio/gsettings
    applet.settings_path = applet.get_preferences_path()
    syslog.syslog("settings_path %s" % applet.settings_path)

    box = Gtk.Box()

    #try:
    #   pixbuf = Gtk.IconTheme.get_default().load_icon("document-new", applet.get_size() / 4, 0)
    #   button_icon = Gtk.Image.new_from_pixbuf(pixbuf)
    #except:
    #    print("icon", sys.exc_info())
    #    button_icon = Gtk.Label("Icons")
    #box.add(button_icon)

    #label = Gtk.Label(label="Timer")
    #box.add(label)

    applet.timerarr     = []
    for aa in range(4):
        applet.timerarr.append(0)

    applet.setarr     = []
    applet.setarr.append(10)
    applet.setarr.append(20)
    applet.setarr.append(30)
    applet.setarr.append(40)

    box.add(Gtk.Label(" "))

    applet.bararr     = []
    for aa in range(4):
        barcolor = [.6, .7, .7]
        vb = vertbar(6, applet.get_size(), barcolor)
        applet.bararr.append(vb)
        box.add(vb)

    box.add(Gtk.Label(" "))

    applet.timerlab = Gtk.Label("Timer ")
    box.add(applet.timerlab)
    box.add(Gtk.Label(" "))

    applet.add(box)
    applet.show_all()
    append_menu(applet)

    applet.connect("destroy", destr, was_inst)


# ------------------------------------------------------------------------

idlecnt = 0

def  timex():

    global inst_arr, idlecnt

    #syslogx("timer fired", os.getpid(), time.ctime() )

    cnt = 0
    try:
        for aa in inst_arr:
            if aa:
                cnt += proc_one(aa)
        if cnt == 0:
            #syslog.syslog("no action")
            idlecnt += 1
        else:
            idlecnt = 0
        if idlecnt == 6:
            for aa in inst_arr:
                if aa:
                    aa.timerlab.set_text("Timer")

    except:
        put_exception("In timex:")
        syslog.syslog("exception in timex %s" % str(sys.exc_info()))
        pass

    #  Restart no matter what
    GLib.timeout_add(1000, timex)

barcolarr = [(0., 0., 1.), (0., 1., 0.), (0., .5, 1.), (0., 1., .5), ]

def proc_one(unit):

    cnt = 0
    for aa in range(len(unit.timerarr)):
        #syslog.syslog("Processing %d %d" % (aa, timerarr[aa]))
        if unit.timerarr[aa]:
            unit.timerarr[aa] -= 1
            barcol = barcolarr[aa]
            cent = 100 * unit.timerarr[aa] / unit.setarr[aa]
            unit.bararr[aa].set_procent(cent, barcol)
            cnt += 1

            if unit.timerarr[aa] == 0:
                timer_fired(unit, aa)
    return cnt

def timer_fired(unit, timer_num):
    syslog.syslog("Timer %d alarm" % timer_num)
    ttt = timer_num + 1
    play_sound()
    notify_sys("Timer Countdown Complete", "for Timer Number %d at %s" % (ttt, time.ctime()), 30)
    unit.timerlab.set_text("Alert %d" % ttt)

# Substract current process from display

def destr(obj, instance):
    global inst_arr
    #syslog.syslog("Factory applet destroyed %d" % instance)
    inst_arr[instance] = 0
    #syslog.syslog("inst_arr %s" % str(inst_arr))

# ------------------------------------------------------------------------
# Entry point

def applet_factory(applet, iid, data):

    global  was_inst, inst_arr, gl_applet

    #syslogx("Factory applet", iid)

    if iid != "pgtimer":
       return False

    syslogx(" ========= Started applet", os.getpid(), time.ctime())

    applet_fill(applet)
    was_inst += 1
    inst_arr.append(applet)
    GLib.timeout_add(1000, timex)
    return True

#print(dir(MatePanelApplet.Applet))

# ------------------------------------------------------------------------
# Start the whole

MatePanelApplet.Applet.factory_main("pgtimerFactory", True,
                                    MatePanelApplet.Applet.__gtype__,
                                    applet_factory, None)

# EOF
