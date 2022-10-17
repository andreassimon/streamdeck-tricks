import os
from subprocess import Popen

import gi

from appindicator.CountdownPromptDialog import CountdownPromptDialog

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, AppIndicator3

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class Countdown:
    INSTANCE = None

    def __init__(self):
        self.countdown_process = None

    def to_28_10_22(self, _=None):
        if self.countdown_process:
            self.countdown_process.terminate()
        self.countdown_process = Popen(['/bin/bash', './countdown-with-weeks.bash', '-d', "Oct 28 2022 15:00"],
                                       cwd=MODULE_PATH,
                                       env={"TERM": "screen-256color"})

    def some_minutes(self, _=None):
        if self.countdown_process:
            self.countdown_process.terminate()
        minutes = self.prompt_for_minutes()
        if int(minutes) > 0:
            self.countdown_process = Popen(['/bin/bash', './countdown-with-hours.bash', '-m', minutes],
                                           cwd=MODULE_PATH,
                                           env={"TERM": "screen-256color"})

    @staticmethod
    def prompt_for_minutes():
        dialog = CountdownPromptDialog()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            minutes = dialog.minutes.get_text()
        else:
            minutes = -1
        dialog.destroy()
        return minutes

    def exit(self):
        if self.countdown_process:
            self.countdown_process.terminate()

    @classmethod
    def instance(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = Countdown()
        return cls.INSTANCE


class AppIndicator:

    def __init__(self, streamdecks, onexit):
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

        pavucontrol_tray = Gtk.MenuItem(label='Pulse Audio Volume Controls')
        pavucontrol_tray.connect('activate', self.tray_pavucontrol)
        menu.append(pavucontrol_tray)

        countdown_to_28_10_22_tray = Gtk.MenuItem(label='Pause bis 28.10.2022')
        countdown_to_28_10_22_tray.connect('activate', self.countdown.to_28_10_22)
        menu.append(countdown_to_28_10_22_tray)

        countdown_10min = Gtk.MenuItem(label='Pause für ...')
        countdown_10min.connect('activate', self.countdown.some_minutes)
        menu.append(countdown_10min)

        exit_tray = Gtk.MenuItem(label='Quit')
        exit_tray.connect('activate', onexit)
        menu.append(exit_tray)

        # no_decks = Gtk.MenuItem(label='no decks found')
        # menu.append(no_decks)

        menu.show_all()
        return menu

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
        Gtk.main()

    def no_decks_found(self):
        no_decks = Gtk.MenuItem(label='[No decks found!]')
        # no_decks.override_font(Pango.FontDescription.from_string("Cantarell Italic Light 15 `wght`=Bold"))

        self.tray_menu.prepend(no_decks)
        self.tray_menu.show_all()
        self.tray_disconnected(None)
