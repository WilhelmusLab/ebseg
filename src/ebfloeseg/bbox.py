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
            >>> BoundingBoxParser.convert("1,2,3,4")
            BoundingBox(x1=1, y1=2, x2=3, y2=4)

            ..., commas and spaces:
            >>> BoundingBoxParser.convert("1, 2, 3, 4")
            BoundingBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by parentheses:
            >>> BoundingBoxParser.convert("(1,2,3,4)")
            BoundingBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by parentheses and with spaces:
            >>> BoundingBoxParser.convert("(1, 2, 3, 4)")
            BoundingBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by square brackets and with spaces:
            >>> BoundingBoxParser.convert("[1, 2, 3, 4]")
            BoundingBox(x1=1, y1=2, x2=3, y2=4)

            ..., surrounded by square brackets and with spaces:
            >>> BoundingBoxParser.convert("[1, 2, 3, 4]")
            BoundingBox(x1=1, y1=2, x2=3, y2=4)

            We can do the same with floats:
            >>> BoundingBoxParser.convert("1.2,2.4,3,4")
            BoundingBox(x1=1.2, y1=2.4, x2=3, y2=4)

            We can do the same with floats:
            >>> BoundingBoxParser.convert("(1.2,  2.4, 3, 4)")
            BoundingBox(x1=1.2, y1=2.4, x2=3, y2=4)




        """
        raw_value = ast.literal_eval(value)
        value = BoundingBox(*raw_value)
        return value
