# Beaufort Sea, Hudson Bay

Run the ebseg pipeline on Beaufort Sea and Hudson Bay.

## Cylc
To run the `cylc` workflow:
```bash
name=beaufort-sea-hudson-bay  # define a name for this run
cylc stop "${name}/*"         # stops any currently running workflows with the name
cylc vip -n ${name} .         # validate & install & play the workflow
cylc tui "${name}"            # opens the text user interface and show just runs of this workflow
```

