import datetime
import pytest
from pathlib import Path
import logging

import rasterio
from ebfloeseg.preprocess import preprocess, preprocess_b, count_blobs_per_label

logger = logging.getLogger(__name__)


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


test_dir = Path(__file__).parent


@pytest.mark.parametrize(
    "truecolorimg,cloudimg,landmask",
    [
        (
            test_dir / "process/truecolor.tiff",
            test_dir / "process/cloud.tiff",
            test_dir / "process/landmask.tiff",
        ),
        (
            test_dir / "input/tci/tci_2012-08-01_214_terra.tiff",
            test_dir / "input/cloud/cloud_2012-08-01_214_terra.tiff",
            test_dir / "input/reproj_land.tiff",
        ),
        (
            test_dir / "input/tci/tci_2012-08-02_215_terra.tiff",
            test_dir / "input/cloud/cloud_2012-08-02_215_terra.tiff",
            test_dir / "input/reproj_land.tiff",
        ),
    ],
)
def test_process_no_duplicated_labels(
    truecolorimg: Path, cloudimg: Path, landmask: Path, tmp_path
):
    preprocess_b(
        ftci=truecolorimg,
        fcloud=cloudimg,
        fland=landmask,
        save_figs=True,
        save_direc=tmp_path,
        fname_prefix="",
        itmax=8,
        itmin=3,
        step=-1,
        erosion_kernel_type="diamond",
        erosion_kernel_size=1,
        date=datetime.date.fromisoformat("2001-01-01"),
    )

    with rasterio.open(tmp_path / "final.tif") as dataset:
        image_array = dataset.read()
        blobs_per_label = count_blobs_per_label(image_array)
        background_label = 0
        for row in blobs_per_label.itertuples():
            if row.label == background_label:
                continue
            logger.debug(row)
            assert (
                row.count == 1
            ), f"{row.count} disconnected components detected for {row.label=}"


if __name__ == "__main__":
    pytest.main()
