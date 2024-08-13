import ast
from collections import namedtuple

import click


BBox = namedtuple("BBox", ["x1", "y1", "x2", "y2"])

class BBoxParser(click.ParamType):
    name = "X1,Y1,X2,Y2"

    @classmethod
    def convert(self, value, param=None, ctx=None):
        """
        Examples:
            We can parse integers separated by commas:
            >>> BBoxParser.convert("1,2,3,4")
            BBox(x1=1, y1=2, x2=3, y2=4)

            ..., commas and spaces:
            >>> BBoxParser.convert("1, 2, 3, 4")
            BBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by parentheses:
            >>> BBoxParser.convert("(1,2,3,4)")
            BBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by parentheses and with spaces:
            >>> BBoxParser.convert("(1, 2, 3, 4)")
            BBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by square brackets and with spaces:
            >>> BBoxParser.convert("[1, 2, 3, 4]")
            BBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by square brackets and with spaces:
            >>> BBoxParser.convert("[1, 2, 3, 4]")
            BBox(x1=1, y1=2, x2=3, y2=4)

            We can do the same with floats:
            >>> BBoxParser.convert("1.2,2.4,3,4")
            BBox(x1=1.2, y1=2.4, x2=3, y2=4)

            We can do the same with floats:
            >>> BBoxParser.convert("(1.2,  2.4, 3, 4)")
            BBox(x1=1.2, y1=2.4, x2=3, y2=4)




        """
        raw_value = ast.literal_eval(value)
        value = BBox(*raw_value)
        return value