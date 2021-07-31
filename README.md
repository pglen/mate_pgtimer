# PG Timer applet for MATE

## Countdown timer

(under construction)

 Install:

sudo install.sh should put all the data in the appropriate directories.

This installer will also kill the old instance .. useful for development

  Usage:

 * Goto panel menu, click on  "Add to Panel"
 * Click on: "PG Timer "

 The python code can emit debug / status statements into syslog. To view them,
open a new terminal and run:

   sudo tail -f /var/log/syslog

See the source for examples of how to emit syslog statements from the panel applet;

Notables:

  This  project is a good template / skeleton platform for MATE applet development, as the
  project contains all the elements for the -- install / code / run / uninstall -- cycle

  It also shows how to populate multiple instances of Applets / Widgets
  from the GLib timer.

  Python is an ideal platform for this kind of task ...

sudo remove.sh should erase all traces of this project from the system.

### Small picture of the contdown timer:

![Image](pgtimer.jpg)

Peter Glen

Contributions welcome
