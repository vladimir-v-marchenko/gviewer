import urwid
from basic import BasicWidget, SearchableText


class Base(object):
    def to_widget(self):
        raise NotImplementedError


class Line(Base):
    """
    One line detail content
    :param content: content
    :type content: str or unicode

    :param style: style name
    :type style: str
    """
    def __init__(self, content):
        self.content = content

    def to_widget(self):
        return SearchableWidget(self.content)


class Prop(Base):
    """
    One line detail content
    :param key: property key
    :type key: str or unicode

    :param value: property value
    :type value: str or unicode

    :param style: style name
    :type style: str
    """
    def __init__(self, key, value):
        self.kv = (key, value)
        self.max_key_length = 0

    def to_widget(self):
        if self.max_key_length:
            format_str = "{0:" + str(self.max_key_length + 1) + "}: "
            return urwid.Text(
                [("view-item key", format_str.format(self.kv[0])),
                 ("view-item value", self.kv[1])])
        return urwid.Text(
            [("view-item key", self.kv[0] + ": "),
             ("view-item value", self.kv[1])])


class Group(object):
    """
    Group the detail content
    :param title: the group title
    :type title: str

    :param items: detail items
    :type items: iterable for Line or Prop
    """
    def __init__(self, title, items, show_title=True):
        self.title = title
        self.items = items
        self.show_title = show_title

    def to_widgets(self):
        widgets = []
        if self.show_title:
            widgets.append(TitleWidget(self.title))
        widgets += [ElementWidget(i) for i in self.items]
        return widgets


class PropsGroup(Group):
    def __init__(self, title, items, *args, **kwargs):
        max_key_length = max(map(lambda p: len(p.kv[0]), items))
        for p in items:
            p.max_key_length = max_key_length
        super(PropsGroup, self).__init__(title, items, *args, **kwargs)


class Groups(Base):
    def __init__(self, groups):
        self.groups = groups

    def to_widget(self):
        return ListWidget(self.groups)


class SearchableWidget(urwid.WidgetWrap):
    def __init__(self, content):
        self.search_widget = SearchableText(content)
        widget = urwid.AttrMap(self.search_widget, "view-item")
        super(SearchableWidget, self).__init__(widget)

    def search_next(self, keyword):
        if self.search_widget.search_next(keyword):
            return True
        return False

    def search_prev(self, keyword):
        if self.search_widget.search_prev(keyword):
            return True
        return False

    def clear_search(self):
        self.search_widget.clear()


class ElementWidget(BasicWidget):
    def __init__(self, item):
        widget = item.to_widget()
        super(ElementWidget, self).__init__(widget=widget)

    def search_next(self, keyword):
        try:
            return self._w.search_next(keyword)
        except AttributeError:
            pass

    def search_prev(self, keyword):
        try:
            return self._w.search_prev(keyword)
        except AttributeError:
            pass

    def clear_search(self):
        if self._w.clear_search:
            self._w.clear_search()


class TitleWidget(BasicWidget):
    def __init__(self, content):
        widget = urwid.Text(content)
        widget = urwid.AttrMap(widget, "view-title")
        super(TitleWidget, self).__init__(widget=widget)


class ListWidget(urwid.WidgetWrap):
    def __init__(self, groups):
        widget = urwid.ListBox(self._make_walker(groups))
        super(ListWidget, self).__init__(widget)
        self._w.set_focus(0)
        self.prev_match = 0

    def _make_walker(self, groups):
        widgets = []
        for group in groups:
            widgets += group.to_widgets()
            widgets.append(EmptyLine())

        if not widgets:
            widgets.append(EmptyLine())

        walker = urwid.SimpleFocusListWalker(widgets)
        return walker

    def search_next(self, keyword):
        curr_index = self._w.get_focus()[1]
        if self.prev_match != curr_index:
            self.clear_prev_search()

        match_index = len(self._w.body) - 1
        for index in range(curr_index, len(self._w.body)):
            try:
                if self._w.body[index].search_next(keyword):
                    match_index = index
                    break
            except AttributeError:
                pass

        self.prev_match = match_index
        self._w.set_focus(match_index)

    def search_prev(self, keyword):
        curr_index = self._w.get_focus()[1]
        if self.prev_match != curr_index:
            self.clear_prev_search()

        match_index = 0
        for index in reversed(range(0, curr_index + 1)):
            try:
                if self._w.body[index].search_prev(keyword):
                    match_index = index
                    break
            except AttributeError:
                pass

        self.prev_match = match_index
        self._w.set_focus(match_index)

    def clear_prev_search(self):
        try:
            self._w.body[self.prev_match].clear_search()
        except AttributeError:
            pass


class EmptyLine(urwid.Text):
    def __init__(self):
        super(EmptyLine, self).__init__("")
