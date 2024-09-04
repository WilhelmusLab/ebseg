import dataclasses
from pathlib import Path
from io import BytesIO

import pytest
import requests_mock

from ebfloeseg.load import load, ImageType, Satellite, DataSet


def are_equal(b1: BytesIO, p2: Path):
    """Check whether two files have identical bytes.

    Arguments:
        b1: io.BytesIO object
        p2: path to a file to be compared with b1
    """
    return b1.read() == Path(p2).read_bytes()


ExampleDataSetBeaufortSea = DataSet(
    datetime="2016-07-01T00:00:00Z",
    wrap="day",
    satellite=Satellite.terra,
    kind=ImageType.truecolor,
    scale=10000,
    bbox=(
        -2330000,
        -420000,
        -1130000,
        750000,
    ),
    crs="EPSG:3413",
    ts=1683675557694,
)


@pytest.mark.smoke
@pytest.mark.slow
@pytest.mark.parametrize("kind", ImageType)
def test_load_runs_in_specific_case_with_validation(kind):
    kwargs = dataclasses.asdict(ExampleDataSetBeaufortSea)
    kwargs.update(kind=kind)
    result = load(**kwargs, format="image/tiff")
    data = BytesIO(result.content)
    assert are_equal(data, Path("tests/load/") / f"{kind.value}.tiff")


@pytest.mark.slow
@pytest.mark.parametrize("satellite", Satellite)
@pytest.mark.parametrize("kind", ImageType)
def test_load_runs_without_crashing_for_different_parameters(kind, satellite):
    load(kind=kind, satellite=satellite, scale=100000)


def test_error_on_empty_file():
    with requests_mock.Mocker() as m:
        m.get(
            "https://wvs.earthdata.nasa.gov/api/v1/snapshot",
            content=Path("tests/load/empty.tiff").read_bytes(),
        )
        with pytest.raises(AssertionError):
            load()
