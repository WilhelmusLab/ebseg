import ast
from typing import NamedTuple

import click


class BoundingBox(NamedTuple):
    x1: int | float
    y1: int | float
    x2: int | float
    y2: int | float


class BoundingBoxParser(click.ParamType):
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
        value = BoundingBox(*raw_value)
        return value
