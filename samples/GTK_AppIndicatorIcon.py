#!/usr/bin/python
import os

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator


def main():
    indicator = appindicator.Indicator.new("customtray", "/home/andreas/Dropbox/OBS/streamdeck-py/elgato_logo_icon.png",
                                           appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu())
    gtk.main()


def menu():
    menu = gtk.Menu()

    show_logs_tray = gtk.MenuItem(label='Show Logs')
    show_logs_tray.connect('activate', show_logs)
    menu.append(show_logs_tray)

    exit_tray = gtk.MenuItem(label='Quit')
    exit_tray.connect('activate', quit)
    menu.append(exit_tray)

    menu.show_all()
    return menu


def show_logs(_):
    os.system("deepin-appstore %U")


def quit(_):
    gtk.main_quit()


if __name__ == "__main__":
    main()
