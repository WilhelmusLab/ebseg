from dataclasses import dataclass
import io
import logging
from collections import namedtuple
from enum import Enum

import numpy as np
import rasterio
import requests
from rasterio.enums import ColorInterp

from ebfloeseg.bbox import BoundingBox

_logger = logging.getLogger(__name__)


class ImageType(str, Enum):
    truecolor = "truecolor"
    cloud = "cloud"
    landmask = "landmask"


class Satellite(str, Enum):
    terra = "terra"
    aqua = "aqua"

def _rescale(x1: int | float, x2: int | float, scale: int | float) -> int:
    """
    
    Examples:
        >>> _rescale(0, 1, 1)
        1
        
        >>> _rescale(0, 10, 10)
        1

        >>> _rescale(0, 100, 10)
        10

    """
    length = abs(x2 - x1)
    rescaled_length = int(length / scale)
    return rescaled_length


def _get_width_height(
    bbox: BoundingBox,
    scale: int | float,
) -> tuple[int, int]:
    """Get width and height for a bounding box where one pixel corresponds to `scale` bounding box units

    Examples:
        >>> _get_width_height(BoundingBox(0, 0, 1, 1), 1)
        (1, 1)

        >>> _get_width_height(BoundingBox(0, 0, 10, 50), 5)
        (2, 10)

    """
    width = _rescale(bbox.x1, bbox.x2, scale)
    height = _rescale(bbox.y1, bbox.y2, scale)
    return width, height


def image_not_empty(img: rasterio.DatasetReader):
    # check that the image isn't all zeros using img.read() and the .colorinterp field
    match img.colorinterp:
        case (ColorInterp.red, ColorInterp.green, ColorInterp.blue):
            red_c, green_c, blue_c = img.read()
        case (ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha):
            red_c, green_c, blue_c, _ = img.read()
        case _:
            msg = "unknown dimensions %s" % img.colorinterp
            raise ValueError(msg)
    return np.any(red_c) or np.any(green_c) or np.any(blue_c)


def alpha_not_empty(img: rasterio.DatasetReader):
    # check that the image isn't all zeros using img.read() and the .colorinterp field
    alpha_index = img.colorinterp.index(ColorInterp.alpha)
    alpha_c = img.read()[alpha_index]
    return np.any(alpha_c)


LoadResult = namedtuple("LoadResult", ["content", "img"])


@dataclass
class DataSet:
    datetime: str
    wrap: str
    satellite: Satellite
    kind: ImageType
    bbox: BoundingBox
    scale: int
    crs: str
    ts: int


ExampleDataSetBeaufortSea = DataSet(
    datetime="2016-07-01T00:00:00Z",
    wrap="day",
    satellite=Satellite.terra,
    kind=ImageType.truecolor,
    scale=250,
    bbox=BoundingBox(
        -2334051,
        -414387,
        -1127689,
        757861,
    ),
    crs="EPSG:3413",
    ts=1683675557694,
)


def load(
    datetime: str = ExampleDataSetBeaufortSea.datetime,
    wrap: str = ExampleDataSetBeaufortSea.wrap,
    satellite: Satellite = ExampleDataSetBeaufortSea.satellite,
    kind: ImageType = ExampleDataSetBeaufortSea.kind,
    bbox: BoundingBox = ExampleDataSetBeaufortSea.bbox,
    scale: int = ExampleDataSetBeaufortSea.scale,
    crs: str = ExampleDataSetBeaufortSea.crs,
    ts: int = ExampleDataSetBeaufortSea.ts,
    format: str = "image/tiff",
    validate: bool = True,
) -> LoadResult:
    """Load an image from the NASA Worldview Snapshots API"""

    match (satellite, kind):
        case (Satellite.terra, ImageType.truecolor):
            layers = "MODIS_Terra_CorrectedReflectance_TrueColor"
        case (Satellite.terra, ImageType.cloud):
            layers = "MODIS_Terra_Cloud_Fraction_Day"
        case (Satellite.aqua, ImageType.truecolor):
            layers = "MODIS_Aqua_CorrectedReflectance_TrueColor"
        case (Satellite.aqua, ImageType.cloud):
            layers = "MODIS_Aqua_Cloud_Fraction_Day"
        case (_, ImageType.landmask):
            layers = "OSM_Land_Mask"
        case _:
            msg = "satellite=%s and image kind=%s not supported" % (satellite, kind)
            raise NotImplementedError(msg)

    width, height = _get_width_height(bbox, scale)
    _logger.info("Width: %s Height: %s" % (width, height))

    url = f"https://wvs.earthdata.nasa.gov/api/v1/snapshot"
    payload = {
        "REQUEST": "GetSnapshot",
        "TIME": datetime,
        "BBOX": f"{bbox.x1},{bbox.y1},{bbox.x2},{bbox.y2}",
        "CRS": crs,
        "LAYERS": layers,
        "WRAP": wrap,
        "FORMAT": format,
        "WIDTH": width,
        "HEIGHT": height,
        "ts": ts,
    }
    r = requests.get(url, params=payload, allow_redirects=True)
    r.raise_for_status()

    img = rasterio.open(io.BytesIO(r.content))

    if validate:
        match (kind):
            case ImageType.truecolor | ImageType.cloud:
                assert image_not_empty(img), "image is empty"
                assert ColorInterp.alpha not in img.colorinterp | alpha_not_empty(
                    img
                ), "alpha channel is empty"
            case ImageType.landmask:
                # An empty landmask is reasonable, nothing to validate here
                pass

    return LoadResult(r.content, img)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load(kind=ImageType.truecolor)
    load(kind=ImageType.cloud)
    load(kind=ImageType.landmask)
