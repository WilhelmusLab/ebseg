from pathlib import Path
from typing import Optional, Union
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
    dtype: Optional[np.dtype] = None,
    res=None,
) -> None:
    profile = tci.profile

    profile.update(
        dtype=dtype,
        count=count,
        compress=compress,
    )

    if res:
        fname = save_direc / f"{res}_{fname}"
    else:
        fname = save_direc / fname

    if rollaxis:
        img = np.rollaxis(img, axis=2)
        axis = None
    else:
        axis = 1

    if img.dtype == np.dtype("bool") or dtype == np.dtype("bool"):
        img_ = img.astype(np.uint8)
        profile.update(
            dtype=img_.dtype,
            nbits=1,
        )

    elif dtype is not None:  # user set the dtype explicitly and it's not a bool
        profile.update(
            dtype=dtype,
        )

    else:  # user didn't set the dtype explicitly – use the image dtype
        profile.update(
            dtype=img.dtype,
        )

    with rasterio.open(fname, "w", **profile) as dst:
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
