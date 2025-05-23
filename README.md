# Segmentation_EB (Original Files)
new segmentation routine used for floe size distribution (FSD) and accurate floe characteristics (Buckley et al., 2024)

Files include:
- Segmentation_EB.ipynb - example notebook with commented seg algorithm code
- input
  - cloud - files for cloud mask
  - tci - images for analysis
  - fci - files for alternative cloud mask (not available yet)
- output
  - sample output

# Packaged version

- Refactored and optimized code
- Notebook using packaged code
- CLI tool `fsdproc` for image processing

## Installation
### Preparation
```sh
python -m venv .venv # create an enviroment for running the package
source .venv/bin/activate # activate the enviroment just created
pip install --upgrade pip # upgrade pip in case it's an old/unsupported version
```
### For regular use
```sh
pip install .
```

### For development

Besides the standard package, extra tooling (e.g., testing, formatting, linting, coverage) can be installed with
```sh
pip install -e ".[dev]"
```

You can also use the included devcontainer, which preinstalls dependencies including:
- GDAL (for `rasterio`) and 
- `libgtk-3-dev` (for `cv2`)
Use the "Reopen in container" command in VSCode or as a GitHub codespace.

## CLI
Upon installation the `fsdproc` command will be available. View its help with `fsdproc --help`.

## Loading and Running
```bash
mkdir -p data/
fsdproc load data/tci.tiff --kind truecolor
fsdproc load data/cld.tiff --kind cloud 
fsdproc load data/lnd.tiff --kind landmask
fsdproc process data/tci.tiff data/cld.tiff data/lnd.tiff data/
```

To get data from Aqua, rather than terra: 
```bash
fsdproc load data/tci.tiff --kind truecolor --satellite aqua
fsdproc load data/cld.tiff --kind cloud --satellite aqua
```