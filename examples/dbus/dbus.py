#!/bin/env python

import subprocess

# three possibilities for DBUS in python:
# * dbus-python (it's legacy and when i tried it, it didn't really work -- missing SessionBus(), ...)
# * pydbus      (seems pretty neat)
# * txdbus      (haven't tried it; apparently it's a native python dbus implementation)
#
#
# official python doc on dbus
# https://wiki.python.org/moin/DbusExamples
#
# pydbus tutorial
# https://github.com/LEW21/pydbus/blob/master/doc/tutorial.rst
from pydbus import SessionBus, SystemBus

# required for the mainloop
from gi.repository import GLib

(rows, cols) = subprocess.check_output(["stty", "size"]).split()
show_introspect = True


def send_desktop_notification(title="Hello World", msg="pydbus works!"):
    """Send a notification to the desktop environment to display"""
    bus = SessionBus()
    notifications = bus.get('.Notifications')
    notifications.Notify('test', 0, 'dialog-information', title, msg, [], {}, 5000)

def list_systemd_units():
    """Fetch all systemd units and print them"""
    bus = SystemBus()

    # systemd is now a proxy for the .systemd1 remote object
    systemd = bus.get(".systemd1")

    for unit in systemd.ListUnits():
        print("Unit:\n")
        print(unit)
        print("-" * int(cols))

def stop_start_systemd_unit(name="ssh.service"):
    """Stop and restart a systemd unit"""
    bus = SystemBus()

    # systemd is now a proxy for the .systemd1 remote object
    systemd = bus.get(".systemd1")
    job1 = systemd.StopUnit(name, "fail")
    job2 = systemd.StartUnit(name, "fail")

def watch_for_new_systemd_jobs():
    """Wait for new systemd units and when they are created, print them out"""
    bus = SystemBus()

    # systemd is now a proxy for the .systemd1 remote object
    systemd = bus.get(".systemd1")
    systemd.JobNew.connect(print)
    GLib.MainLoop().run()

    # or
    #
    # systemd.onJobNew = print
    # GLib.MainLoop.run()

def hibernate():
    try:
        bus = SessionBus()
        power = bus.get('org.gnome.PowerManager', '/org/gnome/PowerManager')

        if power.CanHibernate():
            answer = input("Do you want to hibernate? [Y/n]:")
            if answer.lower() == "y":
                power.Hibernate()

        else:
            print("Cannot hibernate")

    except GLib.Error as e:
        print("Could not get PowerManager from DBUS")


def get_wg_plugin(bus_name="org.freedesktop.NetworkManager.wireguard",
                  object_path="/org/freedesktop/NetworkManager/VPN/Plugin"):
    """Retrieve the wireguard VPN plugin from the System Bus.

    Arguments:
    bus_name -- the bus name of the object to import
    object_path -- the object path of hte object (= where to find the interface)
    """

    # since our wireguard plugin implements the VPN plugin and does not export
    # an interface on its own, we need to use the VPN plugin interfce
    bus = SystemBus()
    wg = bus.get(bus_name, object_path)
    return wg


def wg_disconnect(wg_plugin):
    """Disconnect the WG VPN plugin"""
    wg_plugin.Disconnect()


show_introspect = False

if __name__ == "__main__":
    # send_desktop_notification("Guten Tag", "pydbus funktioniert, mein Herr!")
    # list_systemd_units()
    # hibernate()
    try:
        wg = get_wg_plugin()
        
        if show_introspect:
            print(wg.Introspect())
            help(wg)

        wg_disconnect(wg)

    except Exception as ex:
        print(str(ex))