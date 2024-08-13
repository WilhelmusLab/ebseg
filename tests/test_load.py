from pathlib import Path

import pytest

from ebfloeseg.load import load, ImageType, Satellite


def are_equal(p1, p2):
    return Path(p1).read_bytes() == Path(p2).read_bytes()


@pytest.mark.smoke
@pytest.mark.slow
@pytest.mark.parametrize("kind", ImageType)
def test_load_runs_in_specific_case_with_validation(tmpdir, kind):

    filename = f"{kind.value}.tiff"
    load(tmpdir / filename, kind=kind, scale=10000)
    assert are_equal(tmpdir / filename, Path("tests/load/") / filename)


@pytest.mark.slow
@pytest.mark.parametrize("satellite", Satellite)
@pytest.mark.parametrize("kind", ImageType)
def test_load_runs_without_crashing_for_different_parameters(tmp_path, kind, satellite):
    load(tmp_path / "out.tiff", kind=kind, satellite=satellite, scale=100000)
