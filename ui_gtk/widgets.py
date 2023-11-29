import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gdk

from tree import view
from model import PlotData
from pathlib import Path

from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

import numpy as np


class Confirmation(Gtk.MessageDialog):
    def __init__(self):
        Gtk.MessageDialog.__init__(self)
        self.set_markup('<b>Вы уверены?</b>')
        self.add_button('да', 1)
        self.add_button('нет', 0)


class Window(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('style.css')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        notebook = Gtk.Notebook()

        self.fig = Figure(figsize=(16, 9), dpi=100, constrained_layout=False)
        self.ax = self.fig.add_subplot()
        self.line = None
        self.ani = None

        sw = Gtk.ScrolledWindow()
        sw.set_css_classes(['sw'])

        tab_label = Gtk.Label()
        tab_label.set_text("График")
        notebook.append_page(sw, tab_label)

        tab_label = Gtk.Label()
        tab_label.set_text("JSON")
        notebook.append_page(view, tab_label)
        view.set_css_classes(['view'])
        view.show()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, )
        sw.set_child(vbox)

        box = Gtk.Box(spacing=5)
        vbox.append(box)

        button_add_point = Gtk.Button()
        button_add_point.set_label("Добавить")
        button_add_point.set_css_classes(['button'])
        button_add_point.connect('clicked', self.add_point)

        button_animation_show = Gtk.Button()
        button_animation_show.set_label("Показать")
        button_animation_show.set_css_classes(['button'])
        button_animation_show.connect('clicked', self.animation_on)

        button_animation_hide = Gtk.Button()
        button_animation_hide.set_label("Скрыть")
        button_animation_hide.set_css_classes(['button'])
        button_animation_hide.connect('clicked', self.animation_off)

        self.data = PlotData()

        self.edit_x = Gtk.SpinButton(name="X", value=0)
        self.edit_x.set_css_classes(['button'])
        self.edit_y = Gtk.SpinButton(name="Y", value=0)
        self.edit_y.set_css_classes(['button'])

        for edit in {self.edit_x, self.edit_y}:
            edit.set_adjustment(Gtk.Adjustment(upper=100, step_increment=1, page_increment=10))

        controls = (self.edit_x, self.edit_y, button_add_point, button_animation_show, button_animation_hide)
        for c in controls:
            box.append(c)

        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(800, 600)
        vbox.append(self.canvas)

        page = 0
        if Path('cache.toml').exists():
            with open(Path('cache.toml'), 'r') as f:
                page = int(f.read())

        notebook.set_current_page(page)
        self.notebook = notebook

        self.set_child(notebook)
        self.show()

        self.app = kwargs['application']

        self.connect('close-request', self.handle_exit)

    def add_point(self, *args, **kwargs):
        self.data.add_point(self.edit_x.get_value(), self.edit_y.get_value())
        if self.line is not None:
            self.line.remove()

        self.line, = self.ax.plot(*self.data)
        self.canvas.draw()

    def animation_on(self, *args, **kwargs):
        temp_line, = self.ax.plot(1, 0.5)

        def init():
            temp_line.set_data([], [])
            return temp_line,

        def animate(i):
            x = np.linspace(0, 4, 1000)
            y = (np.sin(2 * np.pi * (x - 0.01 * i)) + 1)
            temp_line.set_data(x, y)
            return temp_line,

        self.ani = animation.FuncAnimation(
            fig=self.fig,
            func=animate,
            init_func=init,
            frames=200,
            interval=20,
            repeat=True
        )

        self.canvas.draw()

    def animation_off(self, *args, **kwargs):
        self.ani.event_source.stop()
        self.ax.cla()
        self.ax.plot(*self.data)
        self.canvas.draw()

    def handle_exit(self, _):
        dialog = Confirmation()  # прицепил к классу метод __del__, первый объект умирает на второй
        # попытке выйти. Т.е. течь не должно, но чуть лишней памяти держит
        dialog.set_transient_for(self)
        dialog.show()
        dialog.connect('response', self.exit)
        return True

    def exit(self, widget, response):
        if response == 1:
            f = open(Path('cache.toml'), 'w+')
            f.write(str(self.notebook.get_current_page()))
            f.close()
            self.app.quit()
        widget.destroy()
