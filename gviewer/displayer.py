from gviewer.view.element import View


class BaseDisplayer(object):  # pragma: no cover
    """ Absctract class for displayer """
    def summary(self, message):
        """ Define how message display in summary widget

        Args:
            message: message that defined at DataStore implementation

        Returns:
            str or unicode or text markup
        """
        return message

    def match(self, keyword, message, summary):
        """ Define is that the message match the keyword

        Default implementation is to check that keyword is contain in summary or not

        Args:
            keyword: str or unicode
            message: message that defined at DataStore implementation
            summary: summary that was generated by to_summary
        Returns:
            bool represent the key is match or not
        """
        return keyword in summary

    def get_views(self):
        """ Define how display message into different views

        Returns:
            list of tuple contans ("view_name", View)
        """
        return [("Undefined", lambda m: View([]))]
