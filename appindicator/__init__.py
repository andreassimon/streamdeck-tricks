import os

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class AppIndicator:

    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "customtray",
            MODULE_PATH + "/tray_icon.png",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.tray_menu())

    def exit(self):
        gtk.main_quit()

    def tray_menu(self):
        menu = gtk.Menu()

        show_logs_tray = gtk.MenuItem(label='Show Logs')
        show_logs_tray.connect('activate', self.tray_show_logs)
        menu.append(show_logs_tray)

        screenshot_tray = gtk.MenuItem(label='Screenshot')
        screenshot_tray.connect('activate', self.tray_screenshot)
        menu.append(screenshot_tray)

        error_tray = gtk.MenuItem(label='Error')
        error_tray.connect('activate', self.tray_error)
        menu.append(error_tray)

        disconnected_tray = gtk.MenuItem(label='Disconnected')
        disconnected_tray.connect('activate', self.tray_disconnected)
        menu.append(disconnected_tray)

        exit_tray = gtk.MenuItem(label='Quit')
        exit_tray.connect('activate', quit)
        menu.append(exit_tray)

        menu.show_all()
        return menu

    def tray_show_logs(self, _):
        os.system("gnome-terminal -- less " + MODULE_PATH + "/../streamdeck-tricks.log")

    def tray_screenshot(self, _):
        os.system("flameshot gui")

    def tray_error(self, _):
        self.tray_icon('tray_icon_error')

    def tray_disconnected(self, _):
        self.tray_icon('tray_icon_disconnected')

    def tray_icon(self, name='tray_icon_error'):
        self.indicator.set_icon_full("{}/{}.png".format(MODULE_PATH, name), name)

    def start(self):
        gtk.main()
