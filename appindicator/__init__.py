import os
import gi

from appindicator import CountdownPromptDialog
from appindicator.Countdown import Countdown

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import GLib, Gtk, AppIndicator3

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class AppIndicator:

    def __init__(self, configure_pulse, streamdecks, onexit):
        self.configure_pulse = configure_pulse
        self.countdown = Countdown.instance()
        self.indicator = AppIndicator3.Indicator.new(
            "customtray",
            MODULE_PATH + "/tray_icon.png",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.streamdecks = streamdecks
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.tray_menu = self.tray_menu(onexit)
        self.indicator.set_menu(self.tray_menu)

    def exit(self):
        self.countdown.exit()
        Gtk.main_quit()

    def tray_menu(self, onexit):
        menu = Gtk.Menu()

        for index, deck in enumerate(self.streamdecks.items()):
            streamdeck_tray = Gtk.MenuItem(label=deck.get_streamdeck_label())
            # streamdeck_tray.connect('activate', self.tray_show_logs)
            menu.append(streamdeck_tray)

        show_logs_tray = Gtk.MenuItem(label='Show Logs')
        show_logs_tray.connect('activate', self.tray_show_logs)
        menu.append(show_logs_tray)

        menu.append(Gtk.SeparatorMenuItem())

        pavucontrol_tray = Gtk.MenuItem(label='Pulse Audio Volume Controls')
        pavucontrol_tray.connect('activate', self.tray_pavucontrol)
        menu.append(pavucontrol_tray)

        pulse_autoconfig_tray = Gtk.MenuItem(label='Pulse Audio autoconfig')
        pulse_autoconfig_tray.connect('activate', self.tray_pulse_autoconfig)
        menu.append(pulse_autoconfig_tray)

        menu.append(Gtk.SeparatorMenuItem())

        countdown_to_28_10_22_tray = Gtk.MenuItem(label='Pause bis 28.10.2022')
        countdown_to_28_10_22_tray.connect('activate', self.countdown.to_28_10_22)
        menu.append(countdown_to_28_10_22_tray)

        countdown_10min = Gtk.MenuItem(label='Pause für ...')
        countdown_10min.connect('activate', self.countdown_some_minutes)
        menu.append(countdown_10min)

        exit_tray = Gtk.MenuItem(label='Quit')
        exit_tray.connect('activate', onexit)
        menu.append(exit_tray)

        # no_decks = Gtk.MenuItem(label='no decks found')
        # menu.append(no_decks)

        menu.show_all()
        return menu

    def countdown_some_minutes(self, _=None):
        GLib.idle_add(self.countdown.some_minutes)

    def tray_show_logs(self, _):
        os.system("gnome-terminal -- less " + MODULE_PATH + "/../streamdeck-tricks.log")

    def tray_pavucontrol(self, _):
        os.system("pavucontrol")

    def tray_pulse_autoconfig(self, _):
        self.configure_pulse()

    def tray_error(self, _error):
        self.tray_icon('tray_icon_error')

    def tray_disconnected(self, _):
        self.tray_icon('tray_icon_disconnected')

    def tray_icon(self, name='tray_icon_error'):
        self.indicator.set_icon_full("{}/{}.png".format(MODULE_PATH, name), name)

    def start(self):
        Gtk.main()

    def no_decks_found(self):
        no_decks = Gtk.MenuItem(label='[No decks found!]')
        # no_decks.override_font(Pango.FontDescription.from_string("Cantarell Italic Light 15 `wght`=Bold"))

        self.tray_menu.prepend(no_decks)
        self.tray_menu.show_all()
        self.tray_disconnected(None)
