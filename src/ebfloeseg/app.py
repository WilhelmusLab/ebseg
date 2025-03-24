#!/usr/bin/env python

import logging
import tomllib
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import pandas
import typer

from ebfloeseg.bbox import BoundingBox, BoundingBoxParser
from ebfloeseg.load import (
    ImageType,
    Satellite,
    ExampleDataSetBeaufortSea as ExampleDataSet,
)
from ebfloeseg.load import load as load_
from ebfloeseg.masking import create_land_mask
from ebfloeseg.preprocess import preprocess, preprocess_b

_logger = logging.getLogger(__name__)

name = "fsdproc"
app = typer.Typer(
    name=name,
    add_completion=False,
    help="""Run the floe size distribution processing by Buckley, E. (2024)

    Buckley, E. M., Cañuelas, L., Timmermans, M.-L., and Wilhelmus, M. M.:
    Seasonal Evolution of the Sea Ice Floe Size Distribution
    from Two Decades of MODIS Data, EGUsphere [preprint],
    https://doi.org/10.5194/egusphere-2024-89, 2024.
    """,
)


@app.callback()
def main(
    quiet: Annotated[
        bool, typer.Option(help="Make the program less talkative.")
    ] = False,
    verbose: Annotated[
        bool, typer.Option(help="Make the program more talkative.")
    ] = False,
    debug: Annotated[
        bool, typer.Option(help="Make the program much more talkative.")
    ] = False,
):
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.WARNING

    logging.basicConfig(level=level)
    return


@app.command(help="Download an image.")
def load(
    outfile: Annotated[Path, typer.Argument()],
    datetime: str = ExampleDataSet.datetime,
    wrap: str = ExampleDataSet.wrap,
    satellite: Satellite = ExampleDataSet.satellite,
    kind: ImageType = ExampleDataSet.kind,
    bbox: Annotated[
        BoundingBox,
        typer.Option(click_type=BoundingBoxParser()),
    ] = ExampleDataSet.bbox,
    scale: Annotated[
        int, typer.Option(help="size of a pixel in units of the bounding box")
    ] = ExampleDataSet.scale,
    crs: str = ExampleDataSet.crs,
    ts: int = ExampleDataSet.ts,
    format: str = "image/tiff",
    validate: Annotated[bool, typer.Option(help="validate the image")] = True,
    cache_directory: Annotated[
        Optional[Path],
        typer.Option(help="location of the cache directory for loaded images"),
    ] = None,
):
    _logger.debug(locals())

    result = load_(
        datetime=datetime,
        wrap=wrap,
        satellite=satellite,
        kind=kind,
        bbox=bbox,
        scale=scale,
        crs=crs,
        ts=ts,
        format=format,
        validate=validate,
        cache_directory=cache_directory,
    )

    with open(outfile, "wb") as f:
        f.write(result.content)

    return


class KernelType(str, Enum):
    diamond = "diamond"
    ellipse = "ellipse"


@app.command(help="Process a single set of true-color, cloud, and landmask images.")
def process(
    truecolorimg: Annotated[Path, typer.Argument()],
    cloudimg: Annotated[Path, typer.Argument()],
    landmask: Annotated[Path, typer.Argument()],
    outdir: Annotated[Path, typer.Argument()],
    save_figs: Annotated[bool, typer.Option()] = True,
    out_prefix: Annotated[
        str, typer.Option(help="string to prepend to filenames")
    ] = "",
    itmax: Annotated[
        int,
        typer.Option(..., "--itmax", help="maximum number of iterations for erosion"),
    ] = 8,
    itmin: Annotated[
        int,
        typer.Option(..., "--itmin", help="minimum number of iterations for erosion"),
    ] = 3,
    step: Annotated[int, typer.Option(..., "--step")] = -1,
    kernel_type: Annotated[
        KernelType, typer.Option(..., "--kernel-type")
    ] = KernelType.diamond,
    kernel_size: Annotated[int, typer.Option(..., "--kernel-size")] = 1,
    date: Annotated[Optional[datetime], typer.Option()] = None,
):
    _logger.debug(locals())

    preprocess_b(
        ftci=truecolorimg,
        fcloud=cloudimg,
        fland=landmask,
        itmax=itmax,
        itmin=itmin,
        step=step,
        erosion_kernel_type=kernel_type,
        erosion_kernel_size=kernel_size,
        save_figs=save_figs,
        save_direc=outdir,
        fname_prefix=out_prefix,
        date=date,
    )

    return


@dataclass
class ConfigParams:
    data_direc: Path
    land: Path
    save_figs: bool
    save_direc: Path
    itmax: int
    itmin: int
    step: int
    kernel_type: str
    kernel_size: int


def validate_kernel_type(ctx: typer.Context, value: str) -> str:
    if value not in ["diamond", "ellipse"]:
        raise typer.BadParameter("Kernel type must be 'diamond' or 'ellipse'")
    return value


def parse_config_file(config_file: Path) -> ConfigParams:

    if not config_file.exists():
        raise FileNotFoundError("Configuration file does not exist.")

    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    defaults = {
        "data_direc": None,  # directory containing TCI and cloud images
        "save_direc": None,  # directory to save figures
        "land": None,  # path to land mask image
        "save_figs": False,  # whether to save figures
        "itmax": 8,  # maximum number of iterations for erosion
        "itmin": 3,  # (inclusive) minimum number of iterations for erosion
        "step": -1,
        "kernel_type": "diamond",  # type of kernel (either diamond or ellipse)
        "kernel_size": 1,
    }

    erosion = config["erosion"]
    config.pop("erosion")
    config.update(erosion)

    for key in defaults:
        if key in config:
            value = config[key]
            if "direc" in key or key == "land":  # Handle paths specifically
                value = Path(value)
            defaults[key] = value

    return ConfigParams(**defaults)


@app.command(
    help="Process a directory of images.",
    epilog=f"Example: {name} --data-direc /path/to/data --save-figs --save-direc /path/to/save --land /path/to/landfile",
)
def process_batch(
    config_file: Path = typer.Option(
        ...,
        "--config-file",
        "-c",
        help="Path to configuration file",
    ),
    max_workers: Optional[int] = typer.Option(
        None,
        help="The maximum number of workers. If None, uses all available processors.",
    ),
):
    _logger.debug(locals())

    args = parse_config_file(config_file)

    save_direc = args.save_direc

    # create output directory
    save_direc.mkdir(exist_ok=True, parents=True)

    # ## land mask
    # this is the same landmask as the original IFT- can be downloaded w SOIT
    land_mask = create_land_mask(args.land)

    # ## load files
    data_direc = args.data_direc
    ftci_direc = data_direc / "tci/"
    fcloud_direc = data_direc / "cloud/"

    # option to save figs after each step
    save_figs = args.save_figs

    ftcis = sorted(Path(ftci_direc).iterdir())
    fclouds = sorted(Path(fcloud_direc).iterdir())

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for ftci, fcloud in zip(ftcis, fclouds):
            future = executor.submit(
                preprocess,
                ftci,
                fcloud,
                land_mask,
                args.itmax,
                args.itmin,
                args.step,
                args.kernel_type,
                args.kernel_size,
                save_figs,
                save_direc,
            )
            futures.append(future)

        # Wait for all threads to complete
        for future in futures:
            future.result()


@app.command(help="Get the bounding box x1, y1, x2, y2 from a CSV file.")
def get_bbox(
    datafile: Annotated[Path, typer.Argument()],
    index: Annotated[str, typer.Argument()],
    index_col: Annotated[str, typer.Option()] = "location",
    colnames: Annotated[list[str], typer.Option()] = [
        "left_x",
        "lower_y",
        "right_x",
        "top_y",
    ],
    separator: Annotated[str, typer.Option()] = ",",
):

    df = pandas.read_csv(datafile, index_col=index_col)
    output = separator.join(str(s) for s in list(df.loc[index][colnames]))
    print(output)


if __name__ == "__main__":
    app()
