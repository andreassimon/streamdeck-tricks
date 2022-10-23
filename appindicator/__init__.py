import os
import gi

from appindicator import CountdownPromptDialog
from appindicator.Countdown import Countdown
from appindicator.app_indicator import AppIndicator

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import AppIndicator3, Gtk, GLib

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class StreamDeckTricksGtk:

    def __init__(self, configure_pulse, decks, quit):
        self.appindicator = AppIndicator(configure_pulse, decks, quit)

    def start(self):
        Gtk.main()

    def exit(self):
        self.appindicator.exit()
        Gtk.main_quit()

    def countdown_some_minutes(self):
        self.appindicator.countdown_some_minutes()

    def show_error(self, error):
        # TODO: Notify about error message
        self.appindicator.tray_error(error)

    def no_decks_found(self):
        self.appindicator.no_decks_found()
