from gi.repository import Gtk
import json

store = Gtk.TreeStore(str)

with open('data.json') as f:
    des = json.load(f)
    their_parent = store.append(None, [list(des.items())[0][0]])
    virus = des['Вирусы']

def recursion(parent, des):
    if type(des) is dict:
        for i1, i2 in des.items():
            new_parent = store.append(parent, [str(i1)])
            recursion(new_parent, i2)
    elif type(des) is list:
        for i2 in des:
            store.append(parent, [str(i2)])
    elif type(des) is str:
        store.append(parent, [str(des)])

recursion(their_parent, virus)
view = Gtk.TreeView(model=store)
renderer = Gtk.CellRendererText()
column = Gtk.TreeViewColumn("Вирусы", renderer, text=0)
view.append_column(column)