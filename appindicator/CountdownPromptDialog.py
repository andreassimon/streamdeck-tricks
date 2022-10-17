import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class CountdownPromptDialog(Gtk.Dialog):
    def __init__(self):
        super().__init__(title="Pause für", flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(150, 100)

        self.minutes = Gtk.Entry()
        self.minutes.set_text("10")
        self.minutes.set_alignment(.5)

        label = Gtk.Label('Minuten')

        self.vbox.pack_start(self.minutes, False, False, 6)
        self.vbox.pack_start(label, False, False, 6)

        self.show_all()
