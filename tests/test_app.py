from pathlib import Path
import subprocess
import filecmp

import pytest
import pandas as pd
import rasterio
import numpy as np

from ebfloeseg.app import parse_config_file


def getdirs(p: Path):
    return [x for x in Path(p).iterdir() if x.is_dir()]


def files_are_equal(file1, file2, chunk_size=1024):
    """
    Check if two files are equal by sequentially comparing their contents.

    Args:
        file1 (str): The path to the first file.
        file2 (str): The path to the second file.

    Returns:
        bool: True if the files are equal, False otherwise.
    """
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        while True:
            b1 = f1.read(chunk_size)
            b2 = f2.read(chunk_size)

            if b1 != b2:
                return False

            if not b1:  # End of file reached
                return True


def are_files_identical(file1, file2):
    return filecmp.cmp(file1, file2, shallow=False)


def are_images_identical(image1_path, image2_path):
    with (
        rasterio.open(str(image1_path)) as img1,
        rasterio.open(str(image2_path)) as img2,
    ):
        return np.array_equal(img1.read(), img2.read())


def are_equal(p1, p2):
    return Path(p1).read_bytes() == Path(p2).read_bytes()


def check_sums(p1, p2):
    s1 = pd.read_csv(p1).to_numpy().sum()
    s2 = pd.read_csv(p2).to_numpy().sum()
    return s1 == s2


# Check final images
def _test_output(tmpdir):
    expdir = Path("tests/expected")
    # Check all tif images, including final and identification rounds
    # -----------------------------------------------------------------
    for d in getdirs(tmpdir):
        for tif in d.glob("*.tif"):
            expected = expdir / tif.relative_to(tmpdir)
            assert are_equal(tif, expected)
            assert are_files_identical(tif, expected)
            assert are_images_identical(tif, expected)

    # Check mask values
    # -----------------------------------------------------------------
    maskvalues214 = tmpdir / "214/mask_values.txt"
    maskvalues214expected = expdir / "214/mask_values.txt"
    assert are_equal(maskvalues214, maskvalues214expected)
    assert are_files_identical(maskvalues214, maskvalues214expected)

    maskvalues215 = tmpdir / "215/mask_values.txt"
    maskvalues215expected = expdir / "215/mask_values.txt"
    assert are_equal(maskvalues215, maskvalues215expected)
    assert are_files_identical(maskvalues215, maskvalues215expected)

    # Check feature extraction
    # -----------------------------------------------------------------
    features214 = tmpdir / "214/2012-08-01_terra_props.csv"
    features214expected = expdir / "214/2012-08-01_terra_props.csv"
    assert check_sums(features214, features214expected)

    features215 = tmpdir / "215/2012-08-02_terra_props.csv"
    features215expected = expdir / "215/2012-08-02_terra_props.csv"
    assert check_sums(features215, features215expected)


@pytest.mark.smoke
@pytest.mark.slow
def test_fsdproc(tmpdir):
    config_file = tmpdir.join("config.toml")
    config_file.write(
        f"""
        data_direc = "tests/input"
        save_figs = true
        save_direc = "{tmpdir}"
        land = "tests/input/reproj_land.tiff"
        [erosion]
        itmax = 8
        itmin = 3
        step = -1
        kernel_type = "diamond"
        kernel_size = 1
        """
    )

    result = subprocess.run(
        [
            "fsdproc",
            "--config-file",
            str(config_file),
            "--max-workers",
            "1",
        ],
        capture_output=True,
        text=True,
    )

    # Check command ran successfully
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"

    _test_output(tmpdir)


def test_parse_config_file(tmpdir):
    config_file = tmpdir.join("config.toml")
    config_file.write(
        """
        data_direc = "/path/to/data"
        save_figs = true
        save_direc = "/path/to/save"
        land = "/path/to/landfile"
        [erosion]
        itmax = 10
        itmin = 5
        step = 2
        kernel_type = "ellipse"
        kernel_size = 3
        """
    )

    params = parse_config_file(config_file)

    assert params.data_direc == Path("/path/to/data")
    assert params.save_figs
    assert params.save_direc == Path("/path/to/save")
    assert params.land == Path("/path/to/landfile")
    assert params.itmax == 10
    assert params.itmin == 5
    assert params.step == 2
    assert params.kernel_type == "ellipse"
    assert params.kernel_size == 3
