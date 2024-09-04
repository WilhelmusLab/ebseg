# Sampled examples

Run the ebseg pipeline on the domains listed in [all-cases.csv](./all-cases.csv).

## Prerequisites

This requires `cylc-rose`. Install using:

```bash
pipx install cylc-rose --include-deps  # this will install cylc and rose
```

## Run with default parameters

To run the `cylc` workflow with the defaults from [rose-suite.conf](./rose-suite.conf), run:
```bash
name=sampled-examples
cylc stop "${name}/*";
cylc vip . -n ${name}
cylc tui ${name}
```

## Run a single example using the workflow

The parameters from rose-suite.conf can be overridden on the command line:

```bash
name=single-example
cylc vip . -n ${name} \
--icp 2004-07-25 --fcp 2004-07-26 \
--set="BBOX='-812500.0,-2112500.0,-712500.0,-2012500.0'" \
--set="LOCATION='baffin_bay'" &&
cylc tui ${name}
```

## Looping through the case list

To loop through a list of cases, and process each at a particular `scale` (in metres):

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

Copy all the output files to the `./output/` directory
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