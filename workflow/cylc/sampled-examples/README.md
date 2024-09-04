# Sampled examples

Run the ebseg pipeline on the domains listed in [all-cases.csv](./all-cases.csv).

## Rose

Installation:

```bash
pipx install cylc-rose --include-deps  # this will install cylc and rose
```

## Cylc
To run the `cylc` workflow with the test data, run:
```bash
name=sampled-examples
cylc stop "${name}/*";
cylc vip . -n ${name}
cylc tui ${name}
```

## OSCAR

The same Cylc configuration can be used on OSCAR, with the settings in `cylc/oscar/global.cylc`.
Install those using:
```bash
mkdir -p ~/.cylc/flow
cp ./cylc/oscar/global.cylc ~/.cylc/flow/global.cylc
```

## Run a single example using the workflow

```bash
name=single-example
cylc vip . -n ${name} \
--icp 2004-07-25 --fcp 2004-07-26 \
--set="BBOX='-812500.0,-2112500.0,-712500.0,-2012500.0'" \
--set="LOCATION='baffin_bay'" &&
cylc tui ${name}
```

## Looping through the case list

Run the processing at a particular scale.

```bash
name=sampled-examples

cylc stop ${name}/*;
cylc clean ${name} -y

scale=250
datafile="all-cases.csv"
index_col="fullname"
for fullname in $(pipx run util/get_fullnames.py "${datafile}" "${index_col}" --start 50 --stop 53); 
do   
  cylc vip . -n ${name} --run-name=${fullname}-${scale}m $(pipx run util/template.py ${datafile} ${index_col} ${fullname}); 
done

cylc tui
```

Copy all the output files to the /output directory
```bash
rundir="${HOME}/cylc-run/${name}"
targetdir="output/${scale}m/"
mkdir -p ${targetdir}
for dir in ${rundir}/*/share/*/
do
  cp -r $dir ${targetdir}
  sleep 0.01
done
```