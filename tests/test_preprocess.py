import datetime
import os
import pytest
from pathlib import Path
import shutil

import numpy as np
import rasterio
import skimage.measure

from ebfloeseg.preprocess import preprocess, preprocess_b 


def test_process_exception(tmpdir):
    fcloud = "cloud.tif"
    ftci = "tci.tif"
    fcloud_direc = Path(tmpdir, "clouds")
    ftci_direc = Path(tmpdir, "tcis")
    save_figs = True
    save_direc = tmpdir
    land_mask = "land_mask.tif"
    erode_itmax = 8
    erode_itmin = 3
    step = -1
    erosion_kernel_type = "diamond"
    erosion_kernel_size = 1

    with pytest.raises(Exception):
        preprocess(
            fcloud,
            ftci,
            fcloud_direc,
            ftci_direc,
            save_figs,
            save_direc,
            land_mask,
            erode_itmax,
            erode_itmin,
            step,
            erosion_kernel_type,
            erosion_kernel_size,
        )


@pytest.fixture
def process_data_directory(tmp_path, date="2012-08-01", day=214, satellite="terra"):
    test_dir = os.path.dirname(__file__)
    shutil.copyfile(Path(f"{test_dir}/input/reproj_land.tiff"), tmp_path / Path("landmask.tiff"))
    shutil.copyfile(Path(f"{test_dir}/input/tci/tci_{date}_{day}_{satellite}.tiff"), tmp_path / Path("truecolor.tiff"))
    shutil.copyfile(Path(f"{test_dir}/input/cloud/cloud_{date}_{day}_{satellite}.tiff"), tmp_path / Path("cloud.tiff"))
    return tmp_path

def test_process_no_duplicated_labels(process_data_directory: Path):
    
    preprocess_b(
        ftci = process_data_directory / "truecolor.tiff",
        fcloud = process_data_directory / "cloud.tiff",
        fland = process_data_directory / "landmask.tiff",
        save_figs = True,
        save_direc = process_data_directory,
        fname_prefix="",
        itmax = 8,
        itmin = 3,
        step = -1,
        erosion_kernel_type = "diamond",
        erosion_kernel_size = 1,
        date=datetime.date.fromisoformat("2001-01-01")
    )

    with rasterio.open(process_data_directory / "final.tif") as dataset:
        image_array = dataset.read()
        for l in np.unique(image_array)[1:]:
            mask = l == image_array
            _, num = skimage.measure.label(mask, return_num=True)
            assert num == 1, f"Disconnected component detected for label {l=}"





if __name__ == "__main__":
    pytest.main()