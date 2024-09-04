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
    Examples:
        >>> import io
        >>> csv = (
        ... '''fullname,location,size,center_lat,center_lon,top_left_lat,top_left_lon,lower_right_lat,lower_right_lon,left_x,right_x,lower_y,top_y,startdate,enddate
        ... 998-beaufort_sea,beaufort_sea,1200km,,,-152.9892,67.6236,-114.8220,78.9424,-2334051,-1127689,-414418,757892,2006-05-04,2006-05-06
        ... 999-beaufort_sea,beaufort_sea,1200km,,,-152.9892,67.6236,-114.8220,78.9424,-2334051,-1127689,-414418,757892,2008-07-13,2008-07-15
        ... ''')
        >>> main(io.StringIO(csv), index_col="fullname", index_val="998-beaufort_sea")
        --icp 2006-05-04 --fcp 2006-05-06 --set BBOX="-2334051,-414418,-1127689,757892" --set LOCATION="beaufort_sea"
        
        >>> main(io.StringIO(csv), index_col="fullname", index_val="999-beaufort_sea")
        --icp 2008-07-13 --fcp 2008-07-15 --set BBOX="-2334051,-414418,-1127689,757892" --set LOCATION="beaufort_sea"

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
