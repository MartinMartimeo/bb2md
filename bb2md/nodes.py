#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""

"""
from collections import defaultdict

__author__ = 'Martin Martimeo <martin@martimeo.de>'
__date__ = '02.07.14 - 17:04'


class BaseNode(object):
    tag = None
    ignore_whitespace = None
    disallow_text = None
    strip_before = None
    full_match = None

    def __init__(self, arg: str):
        self._parent = None
        self._children = []
        self._text = ""

        # Parse arg
        if "=" in arg:
            tag, args = arg.split("=", 1)
            self._args = args.split(",")
        else:
            self._args = []

    def close(self, arg: str):
        if self._text:
            self.appendText(self._text)
        return self._parent

    def appendText(self, text: str) -> bool:

        if self.ignore_whitespace and not text.strip():
            return False

        if self.disallow_text:
            raise TypeError("Node %s disallows in-between text" % type(self))

        self._children.append(text)
        return True

    def append(self, node) -> "BaseNode":

        if isinstance(node, str):
            self._text += node
            return node

        else:
            # Collect text until now as child
            if self._text:
                self.appendText(self._text)
                self._text = ""

            # Append node
            self._children.append(node)
            node._parent = self
            return node

    @classmethod
    def matches(cls, text: str):
        if cls.full_match:
            return cls.tag == text.strip()
        else:
            return text.startswith(cls.tag)

    def markdown(self):
        rtn = ""
        for child in self._children:
            if isinstance(child, str):
                # Escape markdown control sequences
                child = child.replace("*", "\\*").replace("_", "\\_").replace("·", "*")

                # Fold windows line endings together
                child = child.replace("\r\n", "\n").replace("\r", "\n")

                # Remove Magic characters
                child = child.replace('\x94', '').replace('\xa0', '')

                rtn += child
            else:
                if child.strip_before:
                    rtn = rtn.rstrip()
                rtn += child.markdown()
        return rtn


class RootNode(BaseNode):
    pass


class FontNode(BaseNode):
    tag = "font"


class LinkNode(BaseNode):
    tag = "url"

    @property
    def url(self):
        if len(self._args) >= 1:
            return self._args[0]

    def markdown(self):
        if not self.url:
            return "[%s]" % super().markdown()
        else:
            return "[%s](%s)" % (super().markdown(), self.url)


class ColorNode(BaseNode):
    tag = "color"


class FontSizeNode(BaseNode):
    tag = "size"


class BlockNode(BaseNode):
    tag = "block"

    def markdown(self):
        return "\n\n" + super().markdown() + "\n\n"


class UnderlineNode(BaseNode):
    tag = "u"
    full_match = True


class BoldNode(BaseNode):
    tag = "b"
    full_match = True

    def markdown(self):
        return "**" + super().markdown() + "**"


class ItalicNode(BaseNode):
    tag = "i"

    def markdown(self):
        return "_" + super().markdown() + "_"


class ListNode(BaseNode):
    tag = "list"
    ignore_whitespace = True
    disallow_text = True
    strip_before = True

    @property
    def list_type(self):

        try:
            if len(self._args) and int(self._args[0]):
                return "1."
            else:
                return " *"
        except ValueError:
            return " -"

    def markdown(self):
        """
            Lists must be preceeded by an empty line
        :return:
        """
        rtn = "\n\n"
        for child in self._children:

            if isinstance(child, LiNode):
                rtn += child.markdown()
            elif isinstance(child, ListNode):
                rtn = rtn.rstrip()
                rtn_child = child.markdown()
                while rtn_child.startswith("\n\n"):
                    rtn_child = rtn_child[1:]
                for line in rtn_child.split("\n"):
                    rtn += "    " + line + "\n"
            else:
                raise TypeError("Unknown child in list element: %s" % type(child))
        rtn = rtn.rstrip() + "\n\n"
        return rtn


class LiNode(BaseNode):
    tag = "*"

    def markdown(self):
        rtn = ""
        for line in super().markdown().split("\n"):
            rtn += "    " + line + "\n"
        rtn = " %s " % self._parent.list_type + rtn[4:]
        return rtn


class TableNode(BaseNode):
    tag = "table"
    ignore_whitespace = True
    disallow_text = True

    @property
    def width(self):
        if len(self._args) >= 2:
            return self._args[0]
        else:
            return None

    @property
    def height(self):
        if len(self._args) >= 2:
            return self._args[1]
        else:
            return None


    def markdown(self):

        # Convert all elements
        nm = {}
        widths = defaultdict(int)
        heights = defaultdict(int)
        for itr, tr in enumerate(self._children):
            icol = 0
            for itd, td in enumerate(tr._children):
                nm[itr, icol] = td.markdown().split("\n")
                widths[icol] = max(widths[icol], max(len(line) for line in nm[itr, icol]), 1)
                heights[itr] = max(heights[itr], len(nm[itr, icol]), 1)
                if td.rowspan > 1:
                    raise TypeError("Multirow table cells are not supported in markdown")
                icol += td.colspan

        # Print them
        rtn = ""

        # Print first line
        def print_separation():
            r = "+"
            for w in widths.values():
                r += "-" * w
                r += "+"
            r += "\n"
            return r

        rtn += print_separation()
        for itr, height in heights.items():
            for iline in range(0, height):
                rtn += "|"
                for itd, width in widths.items():
                    if not (itr, itd) in nm:
                        line = ""
                    elif len(nm[itr, itd]) > iline:
                        line = nm[itr, itd][iline]
                    else:
                        line = ""
                    rtn += line
                    rtn += (width - len(line)) * ' '
                    rtn += "|"
                rtn += "\n"
            rtn += print_separation()
        return rtn

class TrNode(BaseNode):
    tag = "tr"
    ignore_whitespace = True
    disallow_text = True


class TdNode(BaseNode):
    tag = "td"

    @property
    def colspan(self):
        if len(self._args) >= 4:
            return int(self._args[2]) or 1
        else:
            return 1

    @property
    def rowspan(self):
        if len(self._args) >= 4:
            return int(self._args[3]) or 1
        else:
            return 1
