import gi

gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gtk

from PIL import Image

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class KeyColorPicker(Gtk.Window):
    def __init__(self):
        super().__init__(title="Select Green Values")
        self.clicked_pixels = list()
        self.greens = list()
        self.blues = list()

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        self.event_box = Gtk.EventBox.new()

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(
            '/home/andreas/Dropbox/OBS/streamdeck-py/get_source_screenshot.png')
        self.pimage = Image.open('/home/andreas/Dropbox/OBS/streamdeck-py/get_source_screenshot.png')
        self.canvas = None
        # self.scrolled_window = None

        # https: // pillow.readthedocs.io / en / stable / reference / Image.html  # PIL.Image.frombytes
        # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.frombuffer
        self.image = Gtk.Image.new_from_pixbuf(self.pixbuf)

        self.event_box.add(self.image)
        self.event_box.connect("button_press_event", self.on_image_clicked)

        self.box.pack_start(self.event_box, True, True, 0)

        # Fixing random state for reproducibility
        np.random.seed(19680801)

        N = 50
        x = np.random.rand(N) * 255
        y = np.random.rand(N) * 255

        # self.scatter_plot(x, y)

        self.color = Gtk.ColorButton.new_with_rgba(Gdk.RGBA(0 / 255, 140 / 255, 141 / 255, 255 / 255))
        self.color.set_rgba(Gdk.RGBA(1, 0, 0, 1))
        self.color.set_rgba(Gdk.RGBA(0, 1, 0, 1))

        self.box.pack_start(self.color, True, True, 0)

    def scatter_plot(self, x, y):
        if self.canvas:
            self.box.remove(self.canvas)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.subplot = self.figure.add_subplot()
        self.subplot.set_xlim(0, 255)
        self.subplot.set_ylim(0, 255)
        # t = np.arange(0.0, 3.0, 0.01)
        # s = np.sin(2*np.pi*t)
        # subplot.plot(t, s)
        self.subplot.scatter(x, y)
        # plt.show()
        # self.scrolled_window = Gtk.ScrolledWindow()
        # A scrolled window border goes outside the scrollbars and viewport
        # self.scrolled_window.set_border_width(10)
        self.canvas = FigureCanvas(self.figure)  # a Gtk.DrawingArea
        self.canvas.set_size_request(800, 600)
        self.box.pack_start(self.canvas, True, True, 0)
        # self.scrolled_window.add(self.canvas)
        self.show_all()

    def on_image_clicked(self, widget, event):
        clicked_pixel = self.pimage.getpixel((event.x, event.y))
        self.clicked_pixels.append(clicked_pixel)
        self.greens.append(clicked_pixel[1])
        self.blues.append(clicked_pixel[2])
        print("{} {}".format(self.pimage.mode, clicked_pixel))
        print(self.clicked_pixels)
        print(self.greens)
        print(self.blues)
        self.color.set_rgba(
            Gdk.RGBA(clicked_pixel[0] / 255, clicked_pixel[1] / 255, clicked_pixel[2] / 255, clicked_pixel[3] / 255))

        self.scatter_plot(self.greens, self.blues)



    def on_button1_clicked(self, widget):
        print("Hello")

    def on_button2_clicked(self, widget):
        print("Goodbye")


if __name__ == "__main__":
    win = KeyColorPicker()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
