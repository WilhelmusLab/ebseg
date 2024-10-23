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
    def convert(self, value: str | BoundingBox, param=None, ctx=None):
        """
        Convert a string compatible with the interface for a BoundingBox into a BoundingBox instance

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


            >>> BoundingBoxParser.convert("-2334051.0214676396, -414387.78951688844, -1127689.8419350237, 757861.8364224486")
            BoundingBox(x1=-2334051.0214676396, y1=-414387.78951688844, x2=-1127689.8419350237, y2=757861.8364224486)

            >>> BoundingBoxParser.convert(BoundingBox(-2334051, -414387, -1127689, 757861,))
            BoundingBox(x1=-2334051, y1=-414387, x2=-1127689, y2=757861)

            >>> BoundingBoxParser.convert((1, 2, 3, 4))
            Traceback (most recent call last):
            ...
            NotImplementedError: (1, 2, 3, 4), of type <class 'tuple'>, can't be parsed as a BoundingBox


        """
        if isinstance(value, BoundingBox):
            pass  # the value is the correct type
        elif isinstance(value, str):
            raw_value = ast.literal_eval(value)
            value = BoundingBox(*raw_value)
        else:
            msg = "%s, of type %s, can't be parsed as a BoundingBox" % (
                value,
                type(value),
            )
            raise NotImplementedError(msg)
        return value
