import asyncio
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from .db import init_db, list_channels, add_channel, recent_results
from .worker import Monitor
from .config import DEFAULTS

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="IPTV Monitor")
        self.set_default_size(800, 480)

        self.monitor = None
        self.loop = asyncio.get_event_loop()

        header = Gtk.HeaderBar(title="IPTV Monitor")
        header.set_show_close_button(True)
        self.set_titlebar(header)

        start_btn = Gtk.Button(label='Start Monitor')
        stop_btn = Gtk.Button(label='Stop Monitor')
        start_btn.connect('clicked', self.on_start)
        stop_btn.connect('clicked', self.on_stop)
        header.pack_start(start_btn)
        header.pack_end(stop_btn)

        grid = Gtk.Grid()
        self.add(grid)

        # left: channels and add form
        vleft = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        grid.attach(vleft, 0, 0, 1, 1)

        self.liststore = Gtk.ListStore(int, str, str)
        tree = Gtk.TreeView(self.liststore)
        for i, title in enumerate(['id','name','url']):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=i)
            tree.append_column(col)
        vleft.pack_start(tree, True, True, 0)

        form = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.name_entry = Gtk.Entry(); self.name_entry.set_placeholder_text('Channel name')
        self.url_entry = Gtk.Entry(); self.url_entry.set_placeholder_text('http://.../master.m3u8')
        add_btn = Gtk.Button(label='Add')
        add_btn.connect('clicked', self.on_add)
        form.pack_start(self.name_entry, True, True, 0)
        form.pack_start(self.url_entry, True, True, 0)
        form.pack_start(add_btn, False, False, 0)
        vleft.pack_start(form, False, False, 0)

        # right: details and history
        vright = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        grid.attach(vright, 1, 0, 1, 1)

        self.status_label = Gtk.Label(label='Last run: -')
        vright.pack_start(self.status_label, False, False, 0)

        self.history_store = Gtk.ListStore(str, str, str)
        history_view = Gtk.TreeView(self.history_store)
        for i, title in enumerate(['timestamp','result','notes']):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=i)
            history_view.append_column(col)
        vright.pack_start(history_view, True, True, 0)

        refresh_btn = Gtk.Button(label='Refresh')
        refresh_btn.connect('clicked', lambda b: asyncio.run_coroutine_threadsafe(self.load_data(), self.loop))
        vright.pack_start(refresh_btn, False, False, 0)

        # initialize DB and load
        threading.Thread(target=self._init_async).start()

    def _init_async(self):
        asyncio.run(init_db())
        asyncio.run(self.load_data())

    async def load_data(self):
        self.liststore.clear()
        channels = await list_channels()
        for c in channels:
            self.liststore.append(list(c))

    def on_add(self, _):
        name = self.name_entry.get_text().strip()
        url = self.url_entry.get_text().strip()
        if not name or not url:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, 'Name and URL required')
            dialog.run(); dialog.destroy(); return
        asyncio.run_coroutine_threadsafe(add_channel(name, url), self.loop).result()
        asyncio.run_coroutine_threadsafe(self.load_data(), self.loop)
        self.name_entry.set_text('')
        self.url_entry.set_text('')

    def on_start(self, _):
        if self.monitor and self.monitor._running:
            return
        # run monitor in asyncio background task
        self.monitor = Monitor(None, interval=DEFAULTS['check_interval_sec'])
        # start monitor as background task
        asyncio.run_coroutine_threadsafe(self._start_monitor(), self.loop)

    async def _start_monitor(self):
        self.monitor._running = True
        # start loop task
        self.monitor._task = asyncio.create_task(self.monitor._loop())

    def on_stop(self, _):
        if not self.monitor:
            return
        self.monitor.stop()

def run_app():
    win = MainWindow()
    win.connect('destroy', Gtk.main_quit)
    win.show_all()
    Gtk.main()
