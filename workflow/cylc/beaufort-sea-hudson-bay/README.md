## Cylc
To run the `cylc` workflow with the test data, run:
```bash
name=beaufort-sea-hudson-bay  # define a name for this run
cylc stop "${name}/*"         # stops any currently running workflows with the name
cylc vip -n ${name} .         # validate & install & play the workflow
cylc tui "${name}"            # opens the text user interface and show just runs of this workflow
```

