## Rose

Installation:

```bash
pipx install cylc-rose --include-deps  # this will install cylc and rose
```

## Cylc
To run the `cylc` workflow with the test data, run:
```bash
cylc stop sampled-examples/*;
cylc validate . &&
cylc install . &&
cylc play sampled-examples &&
cylc tui sampled-examples 
```

## OSCAR

The same Cylc configuration can be used on OSCAR, with the settings in `cylc/oscar/global.cylc`.
Install those using:
```bash
mkdir -p ~/.cylc/flow
cp ./cylc/oscar/global.cylc ~/.cylc/flow/global.cylc
```


## Looping through the case list

```bash
cylc stop sampled-examples/*;
cylc install . -n sampled-examples &&
cylc play sampled-examples \
--icp 2004-07-25 --fcp 2004-07-26 \
--set="BBOX='-812500.0,-2112500.0,-712500.0,-2012500.0'" \
--set="LOCATION='baffin_bay'" &&
cylc tui sampled-examples
```


```bash
cylc stop sampled-examples/*;
cylc clean sampled-examples

```

```bash
datafile="all-cases.csv"
index_col="fullname"
for fullname in $(pipx run util/get_fullnames.py "${datafile}" "${index_col}" --start 50); 
do   
  cylc install . --run-name=${fullname}
  cylc play sampled-examples/${fullname} $(pipx run util/template.py ${datafile} ${index_col} ${fullname}); 
done

cylc tui
```

Copy all the output files to the /output directory
```bash
rundir="${HOME}/cylc-run/sampled-examples"
for dir in ${rundir}/*/share/*/
do
  echo $dir
  cp -r $dir output/
  sleep 0.1
done
```

# Running the case list using a 256m pixel size

```bash
touch script.sh && rm script.sh;
scale=256
datafile="all-cases.csv"
index_col="fullname"
for fullname in $(pipx run util/get_fullnames.py "${datafile}" "${index_col}"); 
do   
  echo cylc install . --run-name=${fullname}-${scale}m >> script.sh
  echo cylc play sampled-examples/${fullname}-${scale}m --set SCALE=${scale} $(pipx run util/template.py ${datafile} ${index_col} ${fullname}) >> script.sh ;
done
```

```
bash script.sh

cylc tui
```


Copy all the output files to the /output directory
```bash

rundir="${HOME}/cylc-run/sampled-examples"
targetdir="/oscar/data/mmart119/jholla10/ebseg/output/256m"
for run in ${rundir}/*/
do
  mkdir "${targetdir}/$(basename $run)/"
  
  for datadir in ${run}share/*
  do
    cp -r ${datadir}/ "${targetdir}/$(basename $run)/."
  done;
  sleep 0.1
done;
```