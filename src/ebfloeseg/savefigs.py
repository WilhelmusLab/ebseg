from pathlib import Path
from typing import Union
import logging

import numpy as np
import rasterio
from rasterio import DatasetReader
from numpy.typing import NDArray
from matplotlib import pyplot as plt

_logger = logging.getLogger(__name__)


def imsave(
    tci: DatasetReader,
    img: NDArray,
    save_direc: Path,
    fname: Union[str, Path],
    count: int = 3,
    compress: str = "lzw",
    rollaxis: bool = True,
    as_uint8: bool = False,
    res=None,
) -> None:
    profile = tci.profile
    del profile["dtype"]
    profile.update(
        count=count,
        compress=compress,
    )

    if res:
        fname = save_direc / f"{res}_{fname}"
    else:
        fname = save_direc / fname

    _logger.debug(f"{img.dtype=} {profile=} {img.min()} {img.max()}")

    if rollaxis:
        img = np.rollaxis(img, axis=2)
        axis = None

    else:
        axis = 1

    if img.dtype == np.dtype("bool"):
        img_ = img.astype(np.uint8)
        with rasterio.open(fname, "w", dtype=img_.dtype, nbits=1, **profile) as dst:
            dst.write(img_, axis)
            return

    else:
        with rasterio.open(fname, "w", dtype=img.dtype, **profile) as dst:
            dst.write(img, axis)
            return


def save_ice_mask_hist(
    red_masked,
    bins,
    mincut,
    maxcut,
    target_dir,
    fname: Union[str, Path],
    color="r",
    figsize=(6, 2),
):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    plt.hist(red_masked.flatten(), bins=bins, color=color)
    plt.axvline(mincut)
    plt.axvline(maxcut)
    plt.savefig(target_dir / fname)
    return ax
