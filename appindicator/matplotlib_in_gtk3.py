"""
=================
Embedding in GTK3
=================

Demonstrate adding a FigureCanvasGTK3Agg widget to a Gtk.ScrolledWindow using
GTK3 accessed via pygobject.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np

win = Gtk.Window()
win.connect("delete-event", Gtk.main_quit)
win.set_default_size(400, 300)
win.set_title("Embedding in GTK3")

fig = Figure(figsize=(5, 4), dpi=100)
subplot = fig.add_subplot()
t = np.arange(0.0, 3.0, 0.01)
s = np.sin(2*np.pi*t)
subplot.plot(t, s)

scrolled_window = Gtk.ScrolledWindow()
win.add(scrolled_window)
# A scrolled window border goes outside the scrollbars and viewport
scrolled_window.set_border_width(10)

canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
canvas.set_size_request(800, 600)
scrolled_window.add(canvas)

if __name__ == "__main__":
    win.show_all()
    Gtk.main()
