# !/usr/bin/python
# -*- encoding: utf-8 -*-
"""

"""

__author__ = 'Martin Martimeo <martin@martimeo.de>'
__date__ = '02.07.14 - 16:52'

import logging
logging = logging.getLogger("bb2md")

from .nodes import *


class Bb2MdConverter(object):
    types = {ListNode, LiNode, BlockNode, LinkNode, TableNode, TrNode, TdNode, FontNode, FontSizeNode, BoldNode,
             ItalicNode, ColorNode, UnderlineNode}

    def __init__(self):
        pass

    @classmethod
    def register_type(cls, node_cls):
        cls.types.add(node_cls)

    def __call__(self, bbcode: str):
        """
            Converts a given bbcode to markdown

            :param bbcode:
            :return:
        """

        node = RootNode("")

        i = iter(bbcode)
        while True:
            try:
                c = next(i)
            except StopIteration:
                if not isinstance(node, RootNode):
                    raise TypeError("Unexpected end of string, node is unclosed: %s" % type(node))
                break

            # Just continue parsing
            if not c == "[":
                node.append(c)
                continue

            # Found a [, collect until ]
            arg = ""
            while True:
                d = next(i)
                if d == "]":
                    break
                else:
                    arg += d

            if arg.startswith("/"):
                if node.matches(arg[1:]):
                    node = node.close(arg)
                else:
                    raise TypeError("Unexpected closing tag %s for %s" % (arg, type(node)))
            else:
                # Find a node class handling this
                for cls in self.types:
                    if cls.matches(arg):
                        node = node.append(cls(arg))
                        break
                else:
                    raise TypeError("Could not find handling for %s" % arg)

        node.close("")
        return node.markdown()

    @classmethod
    def convert(cls, bbcode: str):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()

        return cls._instance(bbcode)

