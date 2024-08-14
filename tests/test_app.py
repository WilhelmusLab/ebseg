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


def are_files_identical(file1, file2):
    return filecmp.cmp(file1, file2, shallow=False)


def are_images_identical(image1_path, image2_path):
    with (
        rasterio.open(str(image1_path)) as img1,
        rasterio.open(str(image2_path)) as img2,
    ):
        return np.array_equal(img1.read(), img2.read())


def read_to_df(p1, p2):
    df1 = pd.read_csv(p1)
    df2 = pd.read_csv(p2)
    return df1, df2


# Check final images
def _test_output(tmpdir):
    expdir = Path("tests/expected")
    # Check all tif images, including final and identification rounds, and csv and txt files
    # --------------------------------------------------------------------------------------
    for d in getdirs(tmpdir):
        for file in d.glob(
            "*[!.png]"
        ):  # Exclude png files as they are not created in the original code
            expected = expdir / file.relative_to(tmpdir)
            if file.suffix == ".csv":
                df_file, df_expected = read_to_df(file, expected)
                pd.testing.assert_frame_equal(df_file, df_expected)
                continue
            if file.suffix == ".tif":
                assert are_images_identical(file, expected) # pixel level check
            assert are_files_identical(file, expected)


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
            "process-batch",
            "--config-file",
            str(config_file),
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
