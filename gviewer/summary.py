import urwid

from search import SearchWidget
from basic import BasicWidget

""" Summary Widget Related Component

Contents:

* `SummaryItem`: One line of the SummaryList
* `SummaryListWalker`: The urwid Walker to iterate over the data_store*
* `SummaryList`: urwid ListBox to display Summary

"""


class SummaryItem(urwid.WidgetWrap):
    def __init__(self, parent, displayer, message):
        self.parent = parent
        self.displayer = displayer
        self.message = message
        self.title = self.displayer.to_summary(message)
        super(SummaryItem, self).__init__(self._make_widget())

    def _make_widget(self):
        return urwid.AttrMap(
            urwid.Text(self.title), "summary", "summary focus")

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == "enter":
            self.parent.open_detail(self.message)
            return None
        return key


class SummaryListWalker(urwid.SimpleFocusListWalker):
    def __init__(self, parent, data_store, displayer, content=None):
        super(SummaryListWalker, self).__init__(content or [])
        self.parent = parent
        self.data_store = data_store
        self.displayer = displayer
        data_store.register_walker(self)

    def recv(self, message):
        self.append(SummaryItem(self.parent, self.displayer, message))


class FilterSummaryListWalker(SummaryListWalker):
    def __init__(self, origin_walker, search):
        parent = origin_walker.parent
        data_store = origin_walker.data_store
        displayer = origin_walker.displayer
        content = [m for m in origin_walker if displayer.match(search, m.message, m.title)]
        super(FilterSummaryListWalker, self).__init__(parent, data_store, displayer, content=content)
        self.search = search

    def recv(self, message):
        if self.displayer.match(self.search, message):
            self.append(SummaryItem(self.parent, self.displayer, message))


class SummaryList(BasicWidget):
    def __init__(self, parent, walker):
        self.base_walker = walker
        self.current_walker = walker
        self.list_box = urwid.ListBox(walker)
        self.search = SearchWidget(self)
        widget = urwid.Pile([self.list_box, ("pack", self.search)])
        super(SummaryList, self).__init__(parent, widget)

    def filter(self, search):
        new_walker = FilterSummaryListWalker(self.base_walker, search) if search else self.base_walker
        if new_walker is not self.current_walker:
            self._update(new_walker)

    def _update(self, walker):
        self.current_walker = walker
        self._w.contents.pop(0)
        self._w.contents.insert(0, (urwid.ListBox(walker), self._w.options()))
        self._w.set_focus(0)

    def keypress(self, size, key):
        if key == "/":
            self._w.set_focus(self.search)
            return None
        if key == "q" and isinstance(self.current_walker, FilterSummaryListWalker):
            self.search.clear()
            self.filter(None)
            return None
        return super(SummaryList, self).keypress(size, key)