import gi

gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gtk

from PIL import Image


class KeyColorPicker(Gtk.Window):
    def __init__(self):
        super().__init__(title="Select Green Values")

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        self.button1 = Gtk.Button(label="Hello")
        self.button1.connect("clicked", self.on_button1_clicked)
        self.box.pack_start(self.button1, True, True, 0)

        self.button2 = Gtk.Button(label="Goodbye")
        self.button2.connect("clicked", self.on_button2_clicked)
        self.box.pack_start(self.button2, True, True, 0)

        self.event_box = Gtk.EventBox.new()

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(
            '/home/andreas/Dropbox/OBS/streamdeck-py/get_source_screenshot.png')
        self.pimage = Image.open('/home/andreas/Dropbox/OBS/streamdeck-py/get_source_screenshot.png')

        # https: // pillow.readthedocs.io / en / stable / reference / Image.html  # PIL.Image.frombytes
        # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.frombuffer
        self.image = Gtk.Image.new_from_pixbuf(self.pixbuf)

        self.event_box.add(self.image)
        self.event_box.connect("button_press_event", self.on_image_clicked)

        self.box.pack_start(self.event_box, True, True, 0)

        self.color = Gtk.ColorButton.new_with_rgba(Gdk.RGBA(0 / 255, 140 / 255, 141 / 255, 255 / 255))
        self.color.set_rgba(Gdk.RGBA(1, 0, 0, 1))
        self.color.set_rgba(Gdk.RGBA(0, 1, 0, 1))

        self.box.pack_start(self.color, True, True, 0)

    def on_image_clicked(self, widget, event):
        clicked_pixel = self.pimage.getpixel((event.x, event.y))
        print("{} {}".format(self.pimage.mode, clicked_pixel))
        self.color.set_rgba(
            Gdk.RGBA(clicked_pixel[0] / 255, clicked_pixel[1] / 255, clicked_pixel[2] / 255, clicked_pixel[3] / 255))

    def on_button1_clicked(self, widget):
        print("Hello")

    def on_button2_clicked(self, widget):
        print("Goodbye")


win = KeyColorPicker()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
