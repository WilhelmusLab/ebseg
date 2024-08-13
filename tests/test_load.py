import dataclasses
from pathlib import Path
from io import BytesIO

import pytest
import requests_mock

from ebfloeseg.load import load, ImageType, Satellite, DataSet


def are_equal(b1: BytesIO, p2):
    return b1.read() == Path(p2).read_bytes()


ExampleDataSetBeaufortSea = DataSet(
    datetime="2016-07-01T00:00:00Z",
    wrap="day",
    satellite=Satellite.terra,
    kind=ImageType.truecolor,
    scale=250,
    bbox=(
        -2334051.0214676396,
        -414387.78951688844,
        -1127689.8419350237,
        757861.8364224486,
    ),
    crs="EPSG:3413",
    ts=1683675557694,
)


@pytest.mark.smoke
@pytest.mark.slow
@pytest.mark.parametrize("kind", ImageType)
def test_load_check(kind):
    kwargs = dataclasses.asdict(ExampleDataSetBeaufortSea)
    kwargs.update(kind=kind, scale=10000)
    result = load(**kwargs, format="image/tiff")
    data = BytesIO(result.content)
    assert are_equal(data, Path("tests/load/") / f"{kind.value}.tiff")


@pytest.mark.slow
@pytest.mark.parametrize("satellite", Satellite)
@pytest.mark.parametrize("kind", ImageType)
def test_load(kind, satellite):
    load(kind=kind, satellite=satellite, scale=100000)


def test_error_on_empty_file():
    with requests_mock.Mocker() as m:
        m.get(
            "https://wvs.earthdata.nasa.gov/api/v1/snapshot",
            content=Path("tests/load/empty.tiff").read_bytes(),
        )
        with pytest.raises(AssertionError):
            load()
