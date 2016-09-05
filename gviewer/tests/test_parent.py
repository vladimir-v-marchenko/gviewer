import unittest
import urwid

from .util import render_to_content, render_widgets_to_content, render_to_text
from gviewer.parent import ParentFrame, Footer, Helper, Notification
from gviewer.config import Config
from gviewer.context import Context, DisplayerContext
from gviewer.view.error import ErrorWidget
from gviewer.view.summary import SummaryListWidget
from gviewer.view.detail import DetailWidget
from gviewer.view.element import Line, Group, Groups
from gviewer.store import StaticDataStore


class ParentFrameTest(unittest.TestCase):
    def setUp(self):
        self.messages = [
            ["aaa1", "aaa2", "aaa3"],
            ["bbb1", "bbb2", "bbb3"],
            ["ccc1", "ccc2", "ccc3"]
        ]

        store = StaticDataStore(self.messages)

        context = Context(
            Config(), main_displayer_context=DisplayerContext(store, self))
        self.widget = ParentFrame(context)

        store.setup()

    def summary(self, message):
        return ";".join(message)

    def get_views(self):
        return [
            ("view1", self.view),
            ("view2", self.view)
        ]

    def view(self, message):
        return Groups([Group("foo", [Line(m) for m in message])])

    def test_render(self):
        self.assertEqual(
            render_to_content(self.widget, (30, 10)),
            render_widgets_to_content([
                urwid.AttrMap(urwid.Text("General Viewer"), "header"),
                urwid.AttrMap(urwid.Text(";".join(self.messages[0])), "summary"),
                urwid.AttrMap(urwid.Text(";".join(self.messages[1])), "summary"),
                urwid.AttrMap(urwid.Text(";".join(self.messages[2])), "summary"),
                urwid.Text(""),
                urwid.Text(""),
                urwid.Text(""),
                urwid.Text(""),
                Footer()
            ], (30, 10))
        )

    def test_initial_with_summary(self):
        self.assertIs(
            self.widget.contents["body"][0],
            self.widget.summary
        )
        self.assertIsInstance(
            self.widget.summary,
            SummaryListWidget
        )

    def test_back(self):
        self.widget.open_view(urwid.Text(""))
        self.widget.back()
        self.assertIs(
            self.widget.contents["body"][0],
            self.widget.summary
        )
        self.assertIsInstance(
            self.widget.summary,
            SummaryListWidget
        )

    def test_open_error(self):
        try:
            raise ValueError("error")
        except:
            self.widget.open_error()

        self.assertIsInstance(
            self.widget.contents["body"][0],
            ErrorWidget
        )

    def test_notify(self):
        self.widget.notify("test")

        self.assertEqual(
            render_to_text(self.widget.footer.notification, (5,)),
            ["test "])


class FooterTest(unittest.TestCase):
    def test_render(self):
        widget = Footer()
        self.assertEqual(
            render_to_content(widget, (20, 2)),
            render_widgets_to_content(
                [Helper(), Notification()],
                (20, 2)))

    def test_notify(self):
        widget = Footer()
        widget.notify("test")
        self.assertEqual(
            render_to_text(widget.notification, (5,)),
            ["test "])


class NotificationTest(unittest.TestCase):
    def setUp(self):
        self.widget = Notification()

    def test_render_default(self):
        self.assertEqual(
            render_to_text(self.widget, (5,)),
            ["     "])

    def test_render_notify(self):
        self.widget.notify("test")
        self.assertEqual(
            render_to_text(self.widget, (5,)),
            ["test "])
