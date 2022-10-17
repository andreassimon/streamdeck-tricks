import os
from subprocess import call, Popen
import gi

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk as gtk, AppIndicator3
from gi.repository import Pango

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class AppIndicator:

    def __init__(self, streamdecks, onexit):
        self.countdown_process = None
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
        if self.countdown_process:
            self.countdown_process.terminate()
        gtk.main_quit()

    def tray_menu(self, onexit):
        menu = gtk.Menu()

        for index, deck in enumerate(self.streamdecks.items()):
            streamdeck_tray = gtk.MenuItem(label=deck.get_streamdeck_label())
            # streamdeck_tray.connect('activate', self.tray_show_logs)
            menu.append(streamdeck_tray)

        show_logs_tray = gtk.MenuItem(label='Show Logs')
        show_logs_tray.connect('activate', self.tray_show_logs)
        menu.append(show_logs_tray)

        pavucontrol_tray = gtk.MenuItem(label='Pulse Audio Volume Controls')
        pavucontrol_tray.connect('activate', self.tray_pavucontrol)
        menu.append(pavucontrol_tray)

        countdown_to_28_10_22_tray = gtk.MenuItem(label='Countdown bis 28.10.2022')
        countdown_to_28_10_22_tray.connect('activate', self.tray_countdown_to_28_10_22)
        menu.append(countdown_to_28_10_22_tray)

        countdown_10min = gtk.MenuItem(label='Countdown 10 Minuten')
        countdown_10min.connect('activate', self.tray_countdown_10min)
        menu.append(countdown_10min)

        exit_tray = gtk.MenuItem(label='Quit')
        exit_tray.connect('activate', onexit)
        menu.append(exit_tray)

        # no_decks = gtk.MenuItem(label='no decks found')
        # menu.append(no_decks)

        menu.show_all()
        return menu

    def tray_countdown_to_28_10_22(self, _):
        if self.countdown_process:
            self.countdown_process.terminate()
        self.countdown_process = Popen(['/bin/bash', './countdown-with-weeks.bash', '-d', "Oct 28 2022 15:00"], cwd=MODULE_PATH, env={"TERM": "screen-256color"})

    def tray_countdown_10min(self, _):
        if self.countdown_process:
            self.countdown_process.terminate()
        self.countdown_process = Popen(['/bin/bash', './countdown-with-hours.bash', '-m', '10'], cwd=MODULE_PATH, env={"TERM": "screen-256color"})

    def tray_show_logs(self, _):
        os.system("gnome-terminal -- less " + MODULE_PATH + "/../streamdeck-tricks.log")

    def tray_pavucontrol(self, _):
        os.system("pavucontrol")

    def tray_error(self, _error):
        self.tray_icon('tray_icon_error')

    def tray_disconnected(self, _):
        self.tray_icon('tray_icon_disconnected')

    def tray_icon(self, name='tray_icon_error'):
        self.indicator.set_icon_full("{}/{}.png".format(MODULE_PATH, name), name)

    def start(self):
        gtk.main()

    def no_decks_found(self):
        no_decks = gtk.MenuItem(label='[No decks found!]')
        # no_decks.override_font(Pango.FontDescription.from_string("Cantarell Italic Light 15 `wght`=Bold"))

        self.tray_menu.prepend(no_decks)
        self.tray_menu.show_all()
        self.tray_disconnected(None)
