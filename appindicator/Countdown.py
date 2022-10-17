import os
from subprocess import Popen

from gi.repository import Gtk

from appindicator.CountdownPromptDialog import CountdownPromptDialog


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
        minutes = Countdown.prompt_for_minutes()
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

    @staticmethod
    def instance():
        if not Countdown.INSTANCE:
            Countdown.INSTANCE = Countdown()
        return Countdown.INSTANCE
