# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "typer",
# ]
# ///

import pathlib

import pandas
import typer


def main(datafile: pathlib.Path, index_col: str, index_val: str):
    """
    Get the cylc parameters for a preprocessing run from a CSV file.


    
    Examples:
        >>> import io
        >>> csv = (
        ... '''id,location,center_lat,center_lon,top_left_lat,top_left_lon,lower_right_lat,lower_right_lon,left_x,right_x,lower_y,top_y,startdate,enddate
        ... beaufort_sea,beaufort_sea,75,-135,67.22298,-152.46426,79.32881,-94.68433,-2383879,-883879,-750000,750000,2020-09-05,2020-09-08
        ... hudson_bay,hudson_bay,60,-83,59.65687,-101.24295,57.54266,-66.04186,-2795941,-1295941,-3368686,-1868686,2020-09-06,2020-09-09
        ... ''')
        >>> main(io.StringIO(csv), index_col="id", index_val="beaufort_sea")
        --icp 2020-09-05 --fcp 2020-09-08 --set BBOX="-2383879,-750000,-883879,750000" --set LOCATION="beaufort_sea"
        
        >>> main(io.StringIO(csv), index_col="id", index_val="hudson_bay")
        --icp 2020-09-06 --fcp 2020-09-09 --set BBOX="-2795941,-3368686,-1295941,-1868686" --set LOCATION="hudson_bay"

    """
    df = pandas.read_csv(datafile, index_col=index_col)
    r = df.loc[index_val]
    s = (
        f"--icp {r.startdate} "
        f"--fcp {r.enddate} "
        f"--set BBOX=\"{r.left_x},{r.lower_y},{r.right_x},{r.top_y}\" "
        f"--set LOCATION=\"{r.location}\""
    )
    print(s)



if __name__ == "__main__":
    typer.run(main)
